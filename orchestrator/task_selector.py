"""Task selector for H-Conductor execution loop.

This module provides the TaskSelector class that picks the next ready
task from the queue based on status, dependencies, and priority.

Supports optional ticket validation before task selection (Phase 15).
"""

import logging
from dataclasses import dataclass
from typing import Optional, Callable

from orchestrator.models import TaskModel, QueueModel, TaskStatus

logger = logging.getLogger(__name__)


@dataclass
class SelectionResult:
    """Result of task selection with optional validation.

    Attributes:
        task: Selected task, or None if no task available.
        validation_result: Ticket validation result if validation was run.
        skipped_validation: True if validation was skipped.
    """

    task: Optional[TaskModel]
    validation_result: Optional["TicketValidationResult"] = None  # Forward ref
    skipped_validation: bool = False


class TaskSelector:
    """Selects the next task to execute from a queue.

    Selection criteria:
    - Status must be 'open'
    - All dependencies must be 'complete'
    - Lower priority number = higher priority

    Supports optional ticket validation via validate_before_select flag.

    Example:
        selector = TaskSelector()
        task = selector.get_next_task(queue)
        if task:
            # Execute task

    With validation:
        selector = TaskSelector(validate_tickets=True)
        result = selector.select_with_validation(queue)
        if result.task and result.validation_result.proceed:
            # Execute task
    """

    def __init__(
        self,
        validate_tickets: bool = False,
        strict_tickets: bool = False,
    ):
        """Initialize the selector.

        Args:
            validate_tickets: If True, validate tickets before selection.
            strict_tickets: If True, block execution on HIGH issues.
        """
        self.validate_tickets = validate_tickets
        self.strict_tickets = strict_tickets
        self._validator: Optional["TicketValidator"] = None

    @property
    def validator(self) -> "TicketValidator":
        """Lazy-load the ticket validator."""
        if self._validator is None:
            from orchestrator.ticket_validator import TicketValidator
            self._validator = TicketValidator()
        return self._validator

    def get_next_task(self, queue: QueueModel) -> Optional[TaskModel]:
        """Get the next task ready for execution.

        Args:
            queue: QueueModel containing tasks to select from.

        Returns:
            Next TaskModel ready for execution, or None if no tasks ready.
        """
        if not queue.tasks:
            return None

        # Build set of complete task IDs for dependency checking
        complete_ids = {
            task.id for task in queue.tasks if task.status == TaskStatus.COMPLETE
        }

        # Find all ready tasks (open + dependencies satisfied)
        ready_tasks = []
        for task in queue.tasks:
            if task.status != TaskStatus.OPEN:
                continue

            # Check if all dependencies are complete
            deps_satisfied = all(dep in complete_ids for dep in task.dependencies)
            if deps_satisfied:
                ready_tasks.append(task)

        if not ready_tasks:
            return None

        # Sort by priority (lower number = higher priority)
        ready_tasks.sort(key=lambda t: t.priority)

        return ready_tasks[0]

    def select_with_validation(
        self,
        queue: QueueModel,
        log_path: Optional[str] = None,
    ) -> SelectionResult:
        """Select next task with optional validation.

        Args:
            queue: QueueModel containing tasks to select from.
            log_path: Optional path to write validation log.

        Returns:
            SelectionResult with task and validation info.
        """
        task = self.get_next_task(queue)

        if task is None:
            return SelectionResult(task=None, skipped_validation=True)

        if not self.validate_tickets:
            return SelectionResult(task=task, skipped_validation=True)

        # Validate the selected task
        from orchestrator.ticket_validator import TicketValidationResult
        result = self.validator.validate_ticket(task)

        # Log validation result
        if result.issues:
            logger.info(
                f"Ticket {task.id} validation: "
                f"{result.high_count} HIGH, {result.med_count} MED, {result.low_count} LOW"
            )
            for issue in result.issues:
                level = logging.WARNING if issue.severity == "HIGH" else logging.INFO
                logger.log(level, f"  [{issue.severity}] {issue.dimension}: {issue.issue}")

        # Write to log file if provided
        if log_path:
            self._write_validation_log(log_path, result)

        # In strict mode, block on HIGH issues
        if self.strict_tickets and not result.proceed:
            logger.warning(
                f"Ticket {task.id} blocked by validation (strict mode). "
                f"HIGH issues must be resolved."
            )
            return SelectionResult(
                task=task,
                validation_result=result,
                skipped_validation=False,
            )

        # Non-strict mode: log warning but proceed
        if not result.proceed:
            logger.warning(
                f"Ticket {task.id} has HIGH issues but proceeding (non-strict mode)"
            )

        return SelectionResult(
            task=task,
            validation_result=result,
            skipped_validation=False,
        )

    def _write_validation_log(
        self,
        log_path: str,
        result: "TicketValidationResult",
    ) -> None:
        """Append validation result to log file.

        Args:
            log_path: Path to log file.
            result: Validation result to log.
        """
        from datetime import datetime
        import json
        from pathlib import Path

        log_file = Path(log_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        entry = {
            "timestamp": datetime.now().isoformat(),
            **result.to_dict(),
        }

        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
