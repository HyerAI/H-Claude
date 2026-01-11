"""Memory Agent module for H-Conductor context updates.

This module implements the MemoryAgent class that updates context.yaml
and ROADMAP.yaml after successful task completions. It integrates with
the ModelDispatcher to route summary generation to Opus.

Memory Agent: Goal 6 - "SSoT Integration (Context update)"
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional

import yaml

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from orchestrator.dispatcher import ModelDispatcher


@dataclass
class MemoryUpdateResult:
    """Result of a memory update operation.

    Attributes:
        success: Whether the overall update operation succeeded.
        context_updated: Whether context.yaml was updated.
        roadmap_updated: Whether ROADMAP.yaml was updated.
        summary: Optional AI-generated summary of changes.
        error: Error message if operation failed.
        actions_added: List of action entries added to recent_actions.
    """

    success: bool
    context_updated: bool
    roadmap_updated: bool
    summary: Optional[str] = None
    error: Optional[str] = None
    actions_added: list[str] = field(default_factory=list)


def format_action_entry(task: dict, date: Optional[str] = None) -> str:
    """Format a task as a recent_actions entry.

    Format: "YYYY-MM-DD: TASK_ID - Description"

    Args:
        task: Task dict with 'id' and optional 'description'.
        date: Optional date string (YYYY-MM-DD). Uses today if not provided.

    Returns:
        Formatted action entry string.
    """
    from datetime import date as date_module

    task_id = task.get("id", "UNKNOWN")
    description = task.get("description", "No description")
    date_str = date or date_module.today().isoformat()

    return f"{date_str}: {task_id} - {description}"


def _update_yaml_safely(
    path: str,
    update_fn: Callable[[dict], dict],
    allowed_base_dir: Optional[str] = None,
) -> bool:
    """Safely update a YAML file using atomic read-modify-write pattern.

    Reads the file, applies the update function, and writes back atomically.
    Uses temp file + rename for atomic writes (POSIX-safe).
    Returns False on any error without corrupting the file.

    Args:
        path: Path to the YAML file.
        update_fn: Function that takes current data dict and returns updated dict.
        allowed_base_dir: Optional base directory to restrict file access.
            If provided, path must be within this directory.

    Returns:
        True on success, False on any error (including path traversal attempts).
    """
    file_path = Path(path).resolve()

    # Path traversal prevention
    if allowed_base_dir:
        base = Path(allowed_base_dir).resolve()
        if not str(file_path).startswith(str(base) + "/") and file_path != base:
            logger.warning(f"Path traversal blocked: {file_path} outside {base}")
            return False

    # Check file exists
    if not file_path.exists():
        return False

    try:
        # Read current content
        original_content = file_path.read_text()
        data = yaml.safe_load(original_content)

        if data is None:
            data = {}

        # Apply update
        updated_data = update_fn(data)

        # Atomic write: write to temp file first, then rename
        new_content = yaml.dump(updated_data, default_flow_style=False, allow_unicode=True)
        temp_path = file_path.with_suffix(".tmp")
        temp_path.write_text(new_content)
        temp_path.replace(file_path)  # Atomic rename on POSIX

        return True
    except Exception as e:
        logger.warning(f"YAML update failed for {file_path}: {e}")
        return False


class MemoryAgent:
    """Memory agent for updating context.yaml and ROADMAP.yaml.

    Updates SSoT files after successful task completions to keep
    project state in sync with actual progress.

    Example:
        dispatcher = ModelDispatcher()
        agent = MemoryAgent(dispatcher)
        result = agent.update_context(completed_tasks, context_path)
    """

    def __init__(self, dispatcher: "ModelDispatcher") -> None:
        """Initialize MemoryAgent with a model dispatcher.

        Args:
            dispatcher: ModelDispatcher instance for AI summary generation.
        """
        self.dispatcher = dispatcher

    def update_context(
        self,
        completed_tasks: list[dict],
        context_path: str,
        generate_summary: bool = False,
    ) -> MemoryUpdateResult:
        """Update context.yaml with completed task information.

        Updates:
        - recent_actions: Prepends new entries (rolling 10 max)
        - tasks.completed_this_session: Appends task IDs
        - meta.last_modified: Updates timestamp

        Args:
            completed_tasks: List of task dicts with 'id' and 'description'.
            context_path: Path to context.yaml file.
            generate_summary: If True, generate AI summary via dispatcher.

        Returns:
            MemoryUpdateResult with update status.
        """
        from datetime import date as date_module

        actions_added: list[str] = []

        def do_update(data: dict) -> dict:
            # Ensure required structure exists
            if "meta" not in data:
                data["meta"] = {}
            if "recent_actions" not in data:
                data["recent_actions"] = []
            if "tasks" not in data:
                data["tasks"] = {}
            if "completed_this_session" not in data["tasks"]:
                data["tasks"]["completed_this_session"] = []

            # Update last_modified
            data["meta"]["last_modified"] = date_module.today().isoformat()

            # Add new actions to the front
            for task in completed_tasks:
                entry = format_action_entry(task)
                data["recent_actions"].insert(0, entry)
                actions_added.append(entry)

                # Add task ID to completed_this_session
                task_id = task.get("id", "UNKNOWN")
                if task_id not in data["tasks"]["completed_this_session"]:
                    data["tasks"]["completed_this_session"].append(task_id)

            # Keep only last 10 recent_actions
            data["recent_actions"] = data["recent_actions"][:10]

            return data

        success = _update_yaml_safely(context_path, do_update)

        if not success:
            return MemoryUpdateResult(
                success=False,
                context_updated=False,
                roadmap_updated=False,
                error="Failed to update context.yaml",
            )

        # Generate AI summary if requested
        summary: Optional[str] = None
        if generate_summary:
            summary = self._generate_summary(completed_tasks)

        return MemoryUpdateResult(
            success=True,
            context_updated=True,
            roadmap_updated=False,
            summary=summary,
            actions_added=actions_added,
        )

    def _generate_summary(self, completed_tasks: list[dict]) -> Optional[str]:
        """Generate AI summary of completed tasks.

        Calls the dispatcher with memory_update task type.
        Returns None if dispatcher fails (graceful degradation).

        Args:
            completed_tasks: List of completed task dicts.

        Returns:
            AI-generated summary string, or None on failure.
        """
        try:
            # Format tasks for prompt
            task_list = "\n".join(
                f"- {t.get('id', 'UNKNOWN')}: {t.get('description', 'No description')}"
                for t in completed_tasks
            )

            dispatch_result = self.dispatcher.send_request(
                "memory_update",
                {"completed_tasks": task_list},
            )

            if dispatch_result.success:
                return dispatch_result.response.strip()
            return None
        except Exception as e:
            logger.warning(f"Failed to generate AI summary (non-fatal): {e}")
            return None

    def update_roadmap_status(
        self,
        phase_id: str,
        new_status: str,
        roadmap_path: str,
    ) -> bool:
        """Update the status of a phase in ROADMAP.yaml.

        Updates:
        - phases[].status: Sets the phase status
        - meta.last_updated: Updates timestamp
        - changelog: Appends status change entry

        Args:
            phase_id: ID of the phase to update (e.g., "PHASE-001").
            new_status: New status value (e.g., "complete").
            roadmap_path: Path to ROADMAP.yaml file.

        Returns:
            True on success, False if phase not found or file error.
        """
        from datetime import date as date_module

        phase_found = False

        def do_update(data: dict) -> dict:
            nonlocal phase_found

            # Ensure required structure exists
            if "meta" not in data:
                data["meta"] = {}
            if "phases" not in data:
                data["phases"] = []
            if "changelog" not in data:
                data["changelog"] = []

            # Find and update the phase
            for phase in data["phases"]:
                if phase.get("id") == phase_id:
                    phase["status"] = new_status
                    phase_found = True
                    break

            if not phase_found:
                return data

            # Update last_updated
            today = date_module.today().isoformat()
            data["meta"]["last_updated"] = today

            # Add changelog entry
            data["changelog"].append({
                "date": today,
                "action": "phase_status_update",
                "details": f"{phase_id} marked as {new_status}",
            })

            # Manage active_phases if marking as complete
            if new_status == "complete":
                if "active_phases" not in data:
                    data["active_phases"] = []

                # Remove completed phase from active_phases
                if phase_id in data["active_phases"]:
                    data["active_phases"].remove(phase_id)

                # Add newly unblocked phases
                newly_active = get_next_active_phases(data["phases"], phase_id)
                for new_phase in newly_active:
                    if new_phase not in data["active_phases"]:
                        data["active_phases"].append(new_phase)

                # Keep sorted
                data["active_phases"] = sorted(data["active_phases"])

            return data

        success = _update_yaml_safely(roadmap_path, do_update)

        return success and phase_found


def get_next_active_phases(phases: list[dict], completed_phase_id: str) -> list[str]:
    """Determine which phases become active after a phase completes.

    A phase becomes active when all its dependencies are complete.

    Args:
        phases: List of phase dicts with 'id', 'status', 'dependencies'.
        completed_phase_id: ID of the phase that just completed.

    Returns:
        List of phase IDs that should become active.
    """
    # Build set of completed phase IDs
    completed_ids = {
        p.get("id") for p in phases if p.get("status") == "complete"
    }

    # Find phases that:
    # 1. Are not already complete
    # 2. Depend on the just-completed phase
    # 3. Have all their dependencies satisfied
    newly_active = []

    for phase in phases:
        phase_id = phase.get("id")
        status = phase.get("status")
        dependencies = phase.get("dependencies", [])

        # Skip if already complete
        if status == "complete":
            continue

        # Must depend on the completed phase
        if completed_phase_id not in dependencies:
            continue

        # All dependencies must be complete
        if all(dep in completed_ids for dep in dependencies):
            newly_active.append(phase_id)

    return newly_active
