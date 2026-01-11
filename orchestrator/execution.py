"""Execution module for H-Conductor main loop.

This module provides the core execution components:
- ExecutionContext: Context passed through pipeline stages
- ExecutionResult: Result from task execution
- Stage functions: Individual pipeline stages
- TaskPipeline: Orchestrates stages for a single task
- execution_loop: Main loop that processes queue

PHASE-009: Main Loop Integration
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional, TYPE_CHECKING

from orchestrator.models import TaskModel, TaskStatus
from orchestrator.task_selector import TaskSelector
from orchestrator.queue_manager import QueueManager

if TYPE_CHECKING:
    from orchestrator.dispatcher import ModelDispatcher
    from orchestrator.worktree import WorktreeManager, MergeResult
    from orchestrator.tdd_cycle import TDDFullCycleRunner, CycleResult
    from orchestrator.qa_agent import QAAgent, ReviewResult
    from orchestrator.memory_agent import MemoryAgent, MemoryUpdateResult
    from orchestrator.dna_check import MergeGateResult

logger = logging.getLogger(__name__)


class StageError(Exception):
    """Error during a pipeline stage execution."""

    pass


@dataclass
class ExecutionContext:
    """Context passed through the execution pipeline.

    Contains all data needed for pipeline stages to execute.

    Attributes:
        task: The task being executed.
        worktree_path: Path to the worktree (set after creation).
        branch_name: Git branch name for the task.
        dispatcher: ModelDispatcher for AI generation.
        config: Configuration dictionary.
        queue_path: Optional path to queue.json for DNA check.
        northstar_path: Optional path to NORTHSTAR.md for DNA check.
        worktree_manager: WorktreeManager instance.
        tdd_runner: TDDFullCycleRunner instance.
        qa_agent: QAAgent instance.
        memory_agent: MemoryAgent instance.
    """

    task: TaskModel
    worktree_path: Optional[Path]
    branch_name: str
    dispatcher: "ModelDispatcher"
    config: dict[str, Any]
    queue_path: Optional[str] = None
    northstar_path: Optional[str] = None
    worktree_manager: Optional["WorktreeManager"] = None
    tdd_runner: Optional["TDDFullCycleRunner"] = None
    qa_agent: Optional["QAAgent"] = None
    memory_agent: Optional["MemoryAgent"] = None


@dataclass
class ExecutionResult:
    """Result of executing a task through the pipeline.

    Attributes:
        success: Whether the task completed successfully.
        task_id: ID of the executed task.
        stage_reached: Last stage that completed ('worktree', 'tdd', 'qa', 'dna', 'merge', 'memory', 'cleanup').
        error: Error message if failed.
        tdd_result: Result from TDD cycle (if reached).
        qa_result: Result from QA review (if reached).
        merge_result: Result from merge (if reached).
    """

    success: bool
    task_id: str
    stage_reached: str
    error: Optional[str] = None
    tdd_result: Optional["CycleResult"] = None
    qa_result: Optional["ReviewResult"] = None
    merge_result: Optional["MergeResult"] = None


def stage_create_worktree(
    ctx: ExecutionContext,
    attempt: int = 1,
) -> tuple[Optional[ExecutionContext], Optional[str]]:
    """Pipeline stage: Create worktree for task isolation.

    Args:
        ctx: Execution context with worktree_manager.
        attempt: Attempt number for retry scenarios (default=1).

    Returns:
        Tuple of (updated_context, error).
        On success: (new_ctx with worktree_path, None)
        On failure: (None, error_message)
    """
    if ctx.worktree_manager is None:
        return None, "WorktreeManager not configured"

    try:
        worktree_path = ctx.worktree_manager.create(task_id=ctx.task.id)

        # Create updated context with worktree path
        new_ctx = ExecutionContext(
            task=ctx.task,
            worktree_path=Path(worktree_path),
            branch_name=f"feature/{ctx.task.id}_attempt_{attempt}",
            dispatcher=ctx.dispatcher,
            config=ctx.config,
            queue_path=ctx.queue_path,
            northstar_path=ctx.northstar_path,
            worktree_manager=ctx.worktree_manager,
            tdd_runner=ctx.tdd_runner,
            qa_agent=ctx.qa_agent,
            memory_agent=ctx.memory_agent,
        )

        logger.info(f"Created worktree at {worktree_path} (attempt {attempt})")
        return new_ctx, None

    except Exception as e:
        logger.error(f"Failed to create worktree: {e}")
        return None, f"Disk/Worktree error: {e}"


def stage_run_tdd(
    ctx: ExecutionContext,
) -> tuple[Optional["CycleResult"], Optional[str]]:
    """Pipeline stage: Run TDD cycle (Red -> Green -> Refactor).

    Args:
        ctx: Execution context with tdd_runner.

    Returns:
        Tuple of (CycleResult, error).
        On success: (result, None)
        On failure: (None, error_message)
    """
    if ctx.tdd_runner is None:
        return None, "TDDRunner not configured"

    try:
        # Get target file from task - fail-fast if no files specified
        if not ctx.task.files:
            raise ValueError(f"Task {ctx.task.id} has no files specified")
        target_file = ctx.task.files[0]

        # Run TDD cycle
        ctx.tdd_runner.start_cycle(
            task_id=ctx.task.id,
            task_description=ctx.task.description,
            target_file=target_file,
        )

        ctx.tdd_runner.run_red_phase()
        ctx.tdd_runner.run_green_phase()
        result = ctx.tdd_runner.finish_cycle(skip_refactor=False)

        logger.info(f"TDD cycle complete for {ctx.task.id}")
        return result, None

    except Exception as e:
        logger.error(f"TDD cycle failed: {e}")
        # Abort cycle on error
        if ctx.tdd_runner:
            try:
                ctx.tdd_runner.abort_cycle()
            except Exception as abort_err:
                logger.debug(f"Error during TDD cycle abort (non-fatal): {abort_err}")
        return None, f"TDD failed after max retries: {e}"


def stage_qa_review(
    ctx: ExecutionContext,
    tdd_result: "CycleResult",
) -> tuple[Optional["ReviewResult"], Optional[str]]:
    """Pipeline stage: Run QA review on completed code.

    Args:
        ctx: Execution context with qa_agent.
        tdd_result: Result from TDD cycle.

    Returns:
        Tuple of (ReviewResult, error).
        On success: (result, None)
        On rejection: (result, error_message)
    """
    if ctx.qa_agent is None:
        # Skip QA if not configured
        logger.warning("QA agent not configured, skipping review")
        return None, None

    try:
        # Get code from implementation file
        impl_path = tdd_result.green_result.impl_path if tdd_result.green_result else None
        if impl_path:
            code = Path(impl_path).read_text()
        else:
            code = ""

        test_results = ""
        if tdd_result.green_result:
            test_results = tdd_result.green_result.test_output

        result = ctx.qa_agent.review(
            task={"description": ctx.task.description},
            code=code,
            test_results=test_results,
        )

        if result.decision == "REJECTED":
            return result, f"QA REJECTED: {result.summary}"

        logger.info(f"QA review complete: {result.decision}")
        return result, None

    except Exception as e:
        logger.error(f"QA review failed: {e}")
        return None, f"QA review error: {e}"


def stage_dna_check(
    ctx: ExecutionContext,
) -> tuple[Optional["MergeGateResult"], Optional[str]]:
    """Pipeline stage: Validate DNA traceability to NorthStar.

    Args:
        ctx: Execution context with queue_path and northstar_path.

    Returns:
        Tuple of (MergeGateResult, error).
        On success: (result, None)
        On drift: (result, error_message)
    """
    if not ctx.queue_path or not ctx.northstar_path:
        # Skip DNA check if paths not configured
        logger.warning("DNA check paths not configured, skipping")
        return None, None

    try:
        from orchestrator.dna_check import check_task_before_merge

        result = check_task_before_merge(
            ctx.task.id,
            ctx.queue_path,
            ctx.northstar_path,
        )

        if not result.approved:
            return result, f"DNA drift detected: {result.reason}"

        logger.info(f"DNA check passed: {result.reason}")
        return result, None

    except Exception as e:
        logger.error(f"DNA check failed: {e}")
        return None, f"DNA check error: {e}"


def stage_merge(
    ctx: ExecutionContext,
) -> tuple[Optional["MergeResult"], Optional[str]]:
    """Pipeline stage: Merge worktree changes to main.

    Args:
        ctx: Execution context with worktree_manager.

    Returns:
        Tuple of (MergeResult, error).
        On success: (result, None)
        On conflict: (result, error_message)
    """
    if ctx.worktree_manager is None:
        return None, "WorktreeManager not configured"

    try:
        result = ctx.worktree_manager.merge(task_id=ctx.task.id)

        if not result.success:
            return result, f"Merge failed/conflict: {result.message}"

        logger.info(f"Merge complete: {result.message}")
        return result, None

    except Exception as e:
        logger.error(f"Merge failed: {e}")
        return None, f"Merge error: {e}"


def stage_update_memory(
    ctx: ExecutionContext,
) -> tuple[Optional["MemoryUpdateResult"], Optional[str]]:
    """Pipeline stage: Update context.yaml with task completion.

    This stage is non-blocking - failures are logged but don't fail the pipeline.

    Args:
        ctx: Execution context with memory_agent.

    Returns:
        Tuple of (MemoryUpdateResult, None).
        Never returns error (graceful degradation).
    """
    if ctx.memory_agent is None:
        logger.warning("Memory agent not configured, skipping update")
        return None, None

    try:
        context_path = ctx.config.get("context_path", ".claude/context.yaml")

        result = ctx.memory_agent.update_context(
            completed_tasks=[
                {"id": ctx.task.id, "description": ctx.task.description}
            ],
            context_path=context_path,
        )

        if result.success:
            logger.info(f"Memory updated: {len(result.actions_added)} actions added")
        else:
            logger.warning(f"Memory update failed: {result.error}")

        return result, None

    except Exception as e:
        logger.warning(f"Memory update error (non-fatal): {e}")
        return None, None


def stage_cleanup(ctx: ExecutionContext) -> None:
    """Pipeline stage: Clean up worktree (always runs).

    Args:
        ctx: Execution context with worktree_manager.
    """
    if ctx.worktree_manager is None:
        return

    try:
        ctx.worktree_manager.cleanup(task_id=ctx.task.id, delete_branch=True)
        logger.info(f"Cleanup complete for {ctx.task.id}")
    except Exception as e:
        logger.warning(f"Cleanup error (continuing): {e}")


class TaskPipeline:
    """Orchestrates pipeline stages for a single task.

    Runs stages in order:
    1. worktree - Create isolated worktree
    2. tdd - Run TDD cycle (Red -> Green -> Refactor)
    3. qa - QA review (optional, blocks on rejection)
    4. dna - DNA drift check (optional, blocks on drift)
    5. merge - Merge to main
    6. memory - Update context.yaml (non-blocking)
    7. cleanup - Always runs

    Example:
        pipeline = TaskPipeline(worktree_manager, dispatcher)
        result = pipeline.execute(task)
    """

    def __init__(
        self,
        worktree_manager: "WorktreeManager",
        dispatcher: "ModelDispatcher",
        qa_agent: Optional["QAAgent"] = None,
        memory_agent: Optional["MemoryAgent"] = None,
        tdd_runner_factory: Optional[Callable[..., "TDDFullCycleRunner"]] = None,
        queue_path: Optional[str] = None,
        northstar_path: Optional[str] = None,
        config: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize TaskPipeline.

        Args:
            worktree_manager: WorktreeManager for isolation.
            dispatcher: ModelDispatcher for AI generation.
            qa_agent: Optional QAAgent for code review.
            memory_agent: Optional MemoryAgent for context updates.
            tdd_runner_factory: Factory function to create TDDFullCycleRunner.
            queue_path: Optional path to queue.json for DNA check.
            northstar_path: Optional path to NORTHSTAR.md for DNA check.
            config: Optional configuration dict.
        """
        self.worktree_manager = worktree_manager
        self.dispatcher = dispatcher
        self.qa_agent = qa_agent
        self.memory_agent = memory_agent
        self.tdd_runner_factory = tdd_runner_factory
        self.queue_path = queue_path
        self.northstar_path = northstar_path
        self.config = config or {}

    def execute(self, task: TaskModel) -> ExecutionResult:
        """Execute all pipeline stages for a task.

        Args:
            task: TaskModel to execute.

        Returns:
            ExecutionResult with success status and details.
        """
        ctx: Optional[ExecutionContext] = None
        tdd_result = None
        qa_result = None
        merge_result = None
        stage_reached = "init"
        error_msg = None

        try:
            # Create initial context
            tdd_runner = None
            if self.tdd_runner_factory:
                tdd_runner = self.tdd_runner_factory(
                    worktree_manager=self.worktree_manager,
                    dispatcher=self.dispatcher,
                )

            ctx = ExecutionContext(
                task=task,
                worktree_path=None,
                branch_name="",
                dispatcher=self.dispatcher,
                config=self.config,
                queue_path=self.queue_path,
                northstar_path=self.northstar_path,
                worktree_manager=self.worktree_manager,
                tdd_runner=tdd_runner,
                qa_agent=self.qa_agent,
                memory_agent=self.memory_agent,
            )

            # Stage 1: Create worktree
            stage_reached = "worktree"
            ctx, error = stage_create_worktree(ctx)
            if error:
                error_msg = error
                raise StageError(error)

            # Stage 2: Run TDD
            stage_reached = "tdd"
            tdd_result, error = stage_run_tdd(ctx)
            if error:
                error_msg = error
                raise StageError(error)

            # Stage 3: QA Review (optional)
            if self.qa_agent and tdd_result:
                stage_reached = "qa"
                qa_result, error = stage_qa_review(ctx, tdd_result)
                if error:
                    error_msg = error
                    raise StageError(error)

            # Stage 4: DNA Check (optional)
            if self.queue_path and self.northstar_path:
                stage_reached = "dna"
                _, error = stage_dna_check(ctx)
                if error:
                    error_msg = error
                    raise StageError(error)

            # Stage 5: Merge
            stage_reached = "merge"
            merge_result, error = stage_merge(ctx)
            if error:
                error_msg = error
                raise StageError(error)

            # Stage 6: Update Memory (non-blocking)
            stage_reached = "memory"
            stage_update_memory(ctx)

            # Stage 7: Cleanup
            stage_reached = "cleanup"

            return ExecutionResult(
                success=True,
                task_id=task.id,
                stage_reached=stage_reached,
                tdd_result=tdd_result,
                qa_result=qa_result,
                merge_result=merge_result,
            )

        except StageError:
            return ExecutionResult(
                success=False,
                task_id=task.id,
                stage_reached=stage_reached,
                error=error_msg,
                tdd_result=tdd_result,
                qa_result=qa_result,
            )

        except Exception as e:
            logger.error(f"Unexpected pipeline error: {e}")
            return ExecutionResult(
                success=False,
                task_id=task.id,
                stage_reached=stage_reached,
                error=str(e),
            )

        finally:
            # Cleanup always runs
            if ctx:
                stage_cleanup(ctx)


def execution_loop(
    queue_path: str,
    config: dict[str, Any],
    pipeline: Optional[TaskPipeline] = None,
    max_tasks: Optional[int] = None,
) -> list[ExecutionResult]:
    """Main execution loop that processes tasks from queue.

    Processes tasks until:
    - No more ready tasks
    - max_tasks limit reached
    - Interrupted

    Note: Caller (main.py) is responsible for calling startup_recovery() before
    invoking execution_loop if recovery is desired.

    Args:
        queue_path: Path to queue.json file.
        config: Configuration dictionary.
        pipeline: Optional TaskPipeline (for testing).
        max_tasks: Optional limit on tasks to process.

    Returns:
        List of ExecutionResult for each processed task.
    """
    queue_manager = QueueManager(queue_path)
    selector = TaskSelector()

    results: list[ExecutionResult] = []
    tasks_processed = 0

    while True:
        if max_tasks and tasks_processed >= max_tasks:
            logger.info(f"Reached max_tasks limit: {max_tasks}")
            break

        # Load queue and select next task
        queue = queue_manager.load()
        task = selector.get_next_task(queue)

        if task is None:
            logger.info("No more ready tasks")
            break

        logger.info(f"Processing task: {task.id}")

        # Update status to in_progress
        queue_manager.update_task_status(task.id, TaskStatus.IN_PROGRESS)

        # Execute task
        if pipeline:
            result = pipeline.execute(task)
        else:
            # In production, create pipeline with real components
            result = ExecutionResult(
                success=False,
                task_id=task.id,
                stage_reached="init",
                error="Pipeline not configured",
            )

        results.append(result)
        tasks_processed += 1

        # Update final status
        if result.success:
            queue_manager.update_task_status(task.id, TaskStatus.COMPLETE)
        else:
            queue_manager.update_task_status(task.id, TaskStatus.BLOCKED)

    logger.info(f"Execution loop complete: {tasks_processed} tasks processed")
    return results
