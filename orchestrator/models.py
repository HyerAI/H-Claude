"""Pydantic models for H-Conductor task queue."""

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, model_validator


class TaskStatus(str, Enum):
    """Valid task status values."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETE = "complete"
    BLOCKED = "blocked"
    # HD Interface status values
    CANCELLED = "cancelled"  # Removed from NORTHSTAR (pruned)
    PENDING_REPLAN = "pending_replan"  # Source file changed, needs re-planning
    PENDING_PARENT = "pending_parent"  # Waiting on parent task re-plan


class TaskModel(BaseModel):
    """Model for a single task in the queue.

    DNA Traceability: Every task must have a northstar_goal to trace
    back to the project's guiding principles.
    """

    id: str
    status: TaskStatus
    priority: int
    description: str
    northstar_goal: str = Field(
        ..., description="NorthStar goal this task traces to (DNA traceability)"
    )
    dependencies: list[str] = Field(default_factory=list)
    success_definition: str = ""
    files: list[str] = Field(default_factory=list)
    # HD Interface fields for activation pattern
    source_file: str | None = Field(
        default=None,
        description="Path to SSoT doc (UserStory, ADR, Spec) that activated this task"
    )
    source_hash: str | None = Field(
        default=None,
        description="SHA256 hash of source_file for change detection"
    )


class QueueModel(BaseModel):
    """Model for the task queue (list of tasks with cross-task validation).

    Validates:
    - Unique task IDs
    - Valid dependency references (no orphan dependencies)
    - No circular dependencies
    """

    tasks: list[TaskModel] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_queue(self) -> "QueueModel":
        """Validate cross-task constraints."""
        task_ids = set()
        for task in self.tasks:
            if task.id in task_ids:
                raise ValueError(f"Duplicate task ID: {task.id}")
            task_ids.add(task.id)

        # Check for orphan dependencies
        for task in self.tasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    raise ValueError(
                        f"Task '{task.id}' depends on non-existent task '{dep}'"
                    )

        # Check for circular dependencies using DFS
        self._check_circular_dependencies(task_ids)

        return self

    def _check_circular_dependencies(self, task_ids: set[str]) -> None:
        """Detect circular dependencies using depth-first search."""
        dep_map = {task.id: task.dependencies for task in self.tasks}

        # States: 0 = unvisited, 1 = visiting (in current path), 2 = visited
        state: dict[str, int] = {tid: 0 for tid in task_ids}

        def dfs(task_id: str, path: list[str]) -> None:
            if state[task_id] == 1:
                cycle = path[path.index(task_id) :] + [task_id]
                raise ValueError(f"Circular dependency detected: {' -> '.join(cycle)}")
            if state[task_id] == 2:
                return

            state[task_id] = 1
            path.append(task_id)

            for dep in dep_map.get(task_id, []):
                if dep in task_ids:
                    dfs(dep, path)

            path.pop()
            state[task_id] = 2

        for task_id in task_ids:
            if state[task_id] == 0:
                dfs(task_id, [])
