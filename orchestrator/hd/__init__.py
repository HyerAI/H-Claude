"""HD Interface sub-package - Product Owner layer for H-Conductor.

This package provides the HD Interface layer for human-AI collaboration:
- NORTHSTAR link detection and activation pattern
- Definition of Ready validation
- Hash monitoring for stale spec detection
- Auto-checkbox on task completion
- Dependency cascade on parent reset
- Orphan task pruning
- INBOX.md system messages
"""

from orchestrator.hd.hasher import compute_hash, check_hash_changed, normalize_for_hash
from orchestrator.hd.checkbox import atomic_checkbox_update
from orchestrator.hd.scanner import scan_northstar, get_active_links, prune_orphans
from orchestrator.hd.definition_of_ready import validate_file, ValidationResult
from orchestrator.hd.inbox_writer import InboxWriter
from orchestrator.hd.cascade import reset_task_with_cascade, find_dependents

__all__ = [
    # Hash monitoring
    "compute_hash",
    "check_hash_changed",
    "normalize_for_hash",
    # Auto-checkbox
    "atomic_checkbox_update",
    # Link detection + pruning
    "scan_northstar",
    "get_active_links",
    "prune_orphans",
    # Definition of Ready
    "validate_file",
    "ValidationResult",
    # INBOX writer
    "InboxWriter",
    # Cascade logic
    "reset_task_with_cascade",
    "find_dependents",
]


def check_for_changes(queue_tasks: list, northstar_path: str, inbox_writer: InboxWriter = None) -> list:
    """
    Check for hash changes in source files and cascade resets.

    Args:
        queue_tasks: List of task dicts with source_file and source_hash
        northstar_path: Path to NORTHSTAR.md
        inbox_writer: Optional InboxWriter for logging

    Returns:
        List of task IDs that were reset or paused
    """
    affected = []

    for task in queue_tasks:
        source_file = task.get("source_file")
        stored_hash = task.get("source_hash")

        if not source_file or not stored_hash:
            continue

        if task.get("status") in ("complete", "cancelled"):
            continue

        try:
            if check_hash_changed(source_file, stored_hash):
                # Reset this task and cascade to dependents
                reset_ids = reset_task_with_cascade(
                    task["id"], queue_tasks, inbox_writer
                )
                affected.extend(reset_ids)
        except FileNotFoundError:
            # File was deleted - will be caught by pruning
            pass

    return affected


def on_task_complete(task: dict, northstar_path: str, inbox_writer: InboxWriter = None) -> bool:
    """
    Handle task completion: update checkbox and log to INBOX.

    Args:
        task: Task dict with source_file
        northstar_path: Path to NORTHSTAR.md
        inbox_writer: Optional InboxWriter for logging

    Returns:
        True if checkbox updated successfully
    """
    source_file = task.get("source_file")
    if not source_file:
        return False

    success = atomic_checkbox_update(northstar_path, source_file)

    if inbox_writer:
        if success:
            inbox_writer.log(
                "COMPLETE",
                f"{source_file} delivered.",
                f"Task {task.get('id')} marked complete in NORTHSTAR"
            )
        else:
            inbox_writer.log(
                "ERROR",
                f"Failed to update checkbox for {source_file}",
                "Manual update may be required"
            )

    return success
