"""Dependency cascade logic for task resets.

When a task specification changes and needs re-planning, all tasks
that depend on it must also be marked for re-evaluation.
"""

from collections import deque
from typing import List, Protocol


class InboxWriterProtocol(Protocol):
    """Protocol for inbox writer dependency injection."""

    def log(self, category: str, message: str, action: str | None = None) -> bool:
        """Log a message to the inbox."""
        ...


def find_dependents(task_id: str, queue_tasks: List[dict]) -> List[str]:
    """Find all tasks that directly depend on the given task.

    Args:
        task_id: The task ID to find dependents for.
        queue_tasks: List of task dictionaries.

    Returns:
        List of task IDs that have task_id in their dependencies.
    """
    dependents = []
    for task in queue_tasks:
        deps = task.get("dependencies", [])
        if task_id in deps:
            dependents.append(task.get("id", ""))
    return dependents


def reset_task_with_cascade(
    task_id: str,
    queue_tasks: List[dict],
    inbox_writer: InboxWriterProtocol,
) -> List[str]:
    """Mark a task as pending_replan and cascade to all dependents.

    Args:
        task_id: The task ID to reset.
        queue_tasks: List of task dictionaries (modified in place).
        inbox_writer: Optional writer for logging changes to INBOX.md.

    Returns:
        List of all affected task IDs (including the original).
    """
    # Find the target task
    target = None
    for task in queue_tasks:
        if task.get("id") == task_id:
            target = task
            break

    if target is None:
        return []

    affected: List[str] = []
    visited: set[str] = set()

    # Mark target as pending_replan
    target["status"] = "pending_replan"
    affected.append(task_id)
    visited.add(task_id)
    if inbox_writer:
        inbox_writer.log(
            "CHANGED",
            f"Task {task_id} marked as pending_replan (spec changed)",
        )

    # BFS to find and mark all dependents
    bfs_queue = deque(find_dependents(task_id, queue_tasks))

    while bfs_queue:
        dep_id = bfs_queue.popleft()

        if dep_id in visited:
            continue
        visited.add(dep_id)

        # Find and update the dependent task
        for task in queue_tasks:
            if task.get("id") == dep_id:
                task["status"] = "pending_parent"
                affected.append(dep_id)
                if inbox_writer:
                    inbox_writer.log(
                        "CHANGED",
                        f"Task {dep_id} marked as pending_parent (parent task reset)",
                    )
                # Add this task's dependents to the queue
                bfs_queue.extend(find_dependents(dep_id, queue_tasks))
                break

    return affected
