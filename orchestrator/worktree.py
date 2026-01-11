"""Git Worktree Manager for isolated task execution.

This module provides the WorktreeManager class which handles creating,
managing, and cleaning up git worktrees for isolated task execution.

The worktree isolation is CRITICAL for safety - it ensures worker agents
cannot damage the main repository during execution.

Worktree naming convention:
- Branch: feature/{task_id}_attempt_{n}
- Path: /tmp/hc_worktree_{task_id}
"""

import logging
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from orchestrator.disk_check import check_disk_space, DiskSpaceError

logger = logging.getLogger(__name__)


def _rmtree_onerror(func, path, exc_info):
    """Logging callback for shutil.rmtree errors.

    Logs the error but allows rmtree to continue (equivalent to ignore_errors=True
    but with observability).

    Args:
        func: The function that raised the exception (e.g., os.remove).
        path: The path that caused the error.
        exc_info: Exception info tuple (type, value, traceback).
    """
    logger.warning(f"rmtree error on {path}: {exc_info[1]}")


class WorktreeCreateError(Exception):
    """Raised when worktree creation fails."""

    pass


class WorktreeCleanupError(Exception):
    """Raised when worktree cleanup fails."""

    pass


class WorktreeMergeError(Exception):
    """Raised when worktree merge fails."""

    pass


@dataclass
class MergeResult:
    """Result of a merge operation.

    Attributes:
        success: Whether the merge succeeded.
        message: Descriptive message about the merge result.
    """

    success: bool
    message: str


class WorktreeManager:
    """Manages git worktrees for isolated task execution.

    Creates worktrees in /tmp for task isolation, handles cleanup,
    and provides merge capabilities with fast-forward-only strategy.

    Attributes:
        repo_path: Path to the main git repository.
        worktree_base: Base path for worktree directories (default: /tmp).
    """

    def __init__(
        self,
        repo_path: str,
        worktree_base: str = "/tmp",
        disk_threshold: float = 80.0,
    ) -> None:
        """Initialize WorktreeManager.

        Args:
            repo_path: Path to the main git repository.
            worktree_base: Base path for worktree directories.
            disk_threshold: Maximum disk usage percentage before failing.
        """
        self.repo_path = Path(repo_path).resolve()
        self.worktree_base = Path(worktree_base)
        self.disk_threshold = disk_threshold

    def _get_worktree_path(self, task_id: str) -> Path:
        """Get the worktree path for a task."""
        return self.worktree_base / f"hc_worktree_{task_id}"

    def _get_branch_name(self, task_id: str, attempt: int) -> str:
        """Get the branch name for a task attempt."""
        return f"feature/{task_id}_attempt_{attempt}"

    def create(self, task_id: str, attempt: int = 1) -> str:
        """Create a new worktree for a task.

        Args:
            task_id: Unique identifier for the task.
            attempt: Attempt number (default: 1).

        Returns:
            Path to the created worktree as a string.

        Raises:
            DiskSpaceError: If disk usage exceeds threshold.
            WorktreeCreateError: If git worktree creation fails.
        """
        # Pre-flight disk check
        worktree_path = self._get_worktree_path(task_id)
        check_disk_space(str(self.worktree_base), threshold=self.disk_threshold)

        branch_name = self._get_branch_name(task_id, attempt)

        logger.info(
            f"Creating worktree for task '{task_id}' at {worktree_path} "
            f"with branch '{branch_name}'"
        )

        try:
            # Create the worktree with a new branch
            result = subprocess.run(
                [
                    "git",
                    "worktree",
                    "add",
                    "-b",
                    branch_name,
                    str(worktree_path),
                ],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise WorktreeCreateError(
                    f"Failed to create worktree: {result.stderr}"
                )

            logger.info(f"Worktree created successfully at {worktree_path}")
            return str(worktree_path)

        except WorktreeCreateError:
            # Cleanup any partial state
            self._cleanup_partial_worktree(worktree_path, branch_name)
            raise
        except Exception as e:
            self._cleanup_partial_worktree(worktree_path, branch_name)
            raise WorktreeCreateError(f"Unexpected error creating worktree: {e}")

    def _cleanup_partial_worktree(
        self, worktree_path: Path, branch_name: str
    ) -> None:
        """Clean up any partial state from a failed worktree creation."""
        # Remove directory if it exists
        if worktree_path.exists():
            shutil.rmtree(worktree_path, onerror=_rmtree_onerror)

        # Try to delete the branch if it was created
        subprocess.run(
            ["git", "branch", "-D", branch_name],
            cwd=self.repo_path,
            capture_output=True,
        )

        # Prune worktree metadata
        subprocess.run(
            ["git", "worktree", "prune"],
            cwd=self.repo_path,
            capture_output=True,
        )

    def cleanup(
        self, task_id: str, delete_branch: bool = True, attempt: Optional[int] = None
    ) -> None:
        """Remove a worktree and optionally its branch.

        Args:
            task_id: Task identifier for the worktree to clean.
            delete_branch: Whether to delete the feature branch (default: True).
            attempt: Specific attempt to clean (if None, cleans all attempts).

        Note:
            This method is idempotent - calling it on an already-cleaned
            worktree will not raise an error.
        """
        worktree_path = self._get_worktree_path(task_id)

        logger.info(f"Cleaning up worktree for task '{task_id}'")

        # Remove worktree directory via git
        if worktree_path.exists():
            result = subprocess.run(
                ["git", "worktree", "remove", str(worktree_path), "--force"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                # Try manual removal as fallback
                shutil.rmtree(worktree_path, onerror=_rmtree_onerror)
                subprocess.run(
                    ["git", "worktree", "prune"],
                    cwd=self.repo_path,
                    capture_output=True,
                )

        # Delete branches if requested
        if delete_branch:
            # Find and delete all matching attempt branches
            result = subprocess.run(
                ["git", "branch", "--list", f"feature/{task_id}_attempt_*"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )
            for branch in result.stdout.strip().split("\n"):
                branch = branch.strip()
                if branch:
                    subprocess.run(
                        ["git", "branch", "-D", branch],
                        cwd=self.repo_path,
                        capture_output=True,
                    )
                    logger.info(f"Deleted branch '{branch}'")

        logger.info(f"Cleanup completed for task '{task_id}'")

    def merge(
        self,
        task_id: str,
        target_branch: str = "main",
        attempt: int = 1,
        queue_path: Optional[str] = None,
        northstar_path: Optional[str] = None,
        dna_check: bool = False,
    ) -> MergeResult:
        """Merge worktree changes into target branch using fast-forward only.

        Args:
            task_id: Task identifier for the worktree to merge.
            target_branch: Branch to merge into (default: 'main').
            attempt: Attempt number to merge.
            queue_path: Path to queue.json for DNA check (optional).
            northstar_path: Path to NORTHSTAR.md for DNA check (optional).
            dna_check: Whether to run DNA lineage check before merge (default: False).

        Returns:
            MergeResult with success status and message.

        Note:
            Uses --ff-only strategy. If fast-forward is not possible
            (i.e., there are conflicts), the merge fails and the user
            must resolve conflicts manually.

            When dna_check=True, validates that the task traces to a NorthStar
            goal before allowing the merge. This prevents "orphan features"
            that don't align with project strategy.
        """
        branch_name = self._get_branch_name(task_id, attempt)
        worktree_path = self._get_worktree_path(task_id)

        logger.info(
            f"Attempting to merge branch '{branch_name}' into '{target_branch}'"
        )

        # DNA Drift Check (if enabled)
        if dna_check and queue_path and northstar_path:
            from orchestrator.dna_check import check_task_before_merge, TaskNotFoundError

            logger.info(f"Running DNA drift check for task '{task_id}'")
            try:
                gate_result = check_task_before_merge(task_id, queue_path, northstar_path)
                if not gate_result.approved:
                    logger.warning(f"DNA drift detected: {gate_result.reason}")
                    return MergeResult(
                        success=False,
                        message=f"DNA drift detected - merge blocked: {gate_result.reason}",
                    )
                logger.info(f"DNA check passed: {gate_result.reason}")
            except TaskNotFoundError as e:
                logger.warning(f"Task not found for DNA check: {e}")
                return MergeResult(
                    success=False,
                    message=f"DNA check failed - task not found: {e}",
                )
            except Exception as e:
                logger.error(f"DNA check error: {e}")
                return MergeResult(
                    success=False,
                    message=f"DNA check error: {e}",
                )

        # First, checkout the target branch
        checkout_result = subprocess.run(
            ["git", "checkout", target_branch],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
        )

        if checkout_result.returncode != 0:
            return MergeResult(
                success=False,
                message=f"Failed to checkout '{target_branch}': {checkout_result.stderr}",
            )

        # Attempt fast-forward merge
        merge_result = subprocess.run(
            ["git", "merge", "--ff-only", branch_name],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
        )

        if merge_result.returncode != 0:
            # Merge failed - worktree preserved for debugging
            return MergeResult(
                success=False,
                message=f"Fast-forward merge not possible. "
                f"Please resolve conflicts manually. "
                f"Error: {merge_result.stderr}",
            )

        # Merge successful - cleanup worktree
        logger.info(f"Merge successful, cleaning up worktree")
        self.cleanup(task_id, delete_branch=True)

        return MergeResult(
            success=True,
            message=f"Successfully merged '{branch_name}' into '{target_branch}'",
        )


def find_orphaned_worktrees(repo_path: str) -> list[str]:
    """Find worktrees that are orphaned (stale directories or missing git entries).

    Args:
        repo_path: Path to the main git repository.

    Returns:
        List of paths to orphaned worktree directories.
    """
    repo_path = Path(repo_path).resolve()
    orphaned = []

    # Get list of registered worktrees from git
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )

    registered_paths = set()
    for line in result.stdout.split("\n"):
        if line.startswith("worktree "):
            registered_paths.add(line.split(" ", 1)[1])

    # Find all hc_worktree_* directories in /tmp
    tmp_path = Path("/tmp")
    if tmp_path.exists():
        for path in tmp_path.glob("hc_worktree_*"):
            if path.is_dir():
                path_str = str(path.resolve())
                if path_str not in registered_paths:
                    orphaned.append(path_str)

    # Also find worktrees registered in git but missing from disk
    for reg_path in registered_paths:
        if "hc_worktree_" in reg_path and not Path(reg_path).exists():
            orphaned.append(reg_path)

    return orphaned


def cleanup_orphaned_worktrees(repo_path: str) -> int:
    """Clean up all orphaned worktrees.

    Args:
        repo_path: Path to the main git repository.

    Returns:
        Number of worktrees cleaned up.
    """
    repo_path = Path(repo_path).resolve()
    orphaned = find_orphaned_worktrees(str(repo_path))

    count = 0
    for path in orphaned:
        path_obj = Path(path)
        if path_obj.exists():
            logger.info(f"Removing orphaned worktree directory: {path}")
            shutil.rmtree(path_obj, onerror=_rmtree_onerror)
            count += 1

    # Prune git worktree metadata
    subprocess.run(
        ["git", "worktree", "prune"],
        cwd=repo_path,
        capture_output=True,
    )
    logger.info(f"Ran git worktree prune")

    return count


def startup_recovery(repo_path: str) -> None:
    """Perform startup recovery by cleaning orphaned worktrees.

    Called when the orchestrator starts to clean up any orphaned
    worktrees from previous crashed sessions.

    Args:
        repo_path: Path to the main git repository.
    """
    count = cleanup_orphaned_worktrees(repo_path)
    if count > 0:
        logger.info(f"Recovered {count} orphaned worktrees")
