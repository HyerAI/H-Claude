"""TDD Cycle state machine for Red/Green/Refactor flow.

This module provides the TDDCycle class which orchestrates the TDD
execution flow inside a worktree:
- RED: Generate and verify a failing test
- GREEN: Generate minimal implementation to pass the test
- REFACTOR: Optional cleanup pass

The cycle enforces strict state transitions and tracks history
for debugging and reporting.

TDDCycleExecutor handles the actual execution:
- Dispatches to ModelDispatcher for code generation
- Writes generated code to files
- Runs tests with PytestRunner
- Manages state transitions
"""

import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from orchestrator.dispatcher import ModelDispatcher
    from orchestrator.pytest_runner import PytestRunner
    from orchestrator.retry_policy import RetryPolicy
    from orchestrator.worktree import WorktreeManager

logger = logging.getLogger(__name__)


class CycleState(str, Enum):
    """TDD cycle states."""

    INIT = "init"
    RED = "red"
    GREEN = "green"
    REFACTOR = "refactor"
    DONE = "done"
    FAILED = "failed"


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""

    pass


class InvalidTestError(Exception):
    """Raised when a test passes in RED phase (invalid test)."""

    pass


class NeedsRetryError(Exception):
    """Raised when GREEN phase fails and needs retry."""

    pass


class DispatchError(Exception):
    """Raised when model dispatch fails."""

    pass


class MaxRetriesExceeded(Exception):
    """Raised when max retry attempts are exhausted.

    Attributes:
        retry_count: Number of retry attempts made.
        error_history: List of errors from each attempt.
    """

    def __init__(self, retry_count: int, error_history: list[str]) -> None:
        self.retry_count = retry_count
        self.error_history = error_history
        super().__init__(
            f"Max retries ({retry_count}) exceeded. "
            f"Last error: {error_history[-1] if error_history else 'unknown'}"
        )


@dataclass
class RedResult:
    """Result of the RED phase.

    Attributes:
        test_path: Path to the generated test file.
        test_output: Output from running the test.
        test_failed: Whether the test correctly failed.
    """

    test_path: str
    test_output: str
    test_failed: bool


@dataclass
class GreenResult:
    """Result of the GREEN phase.

    Attributes:
        impl_path: Path to the implementation file.
        test_output: Output from running the test.
        test_passed: Whether the test passed.
    """

    impl_path: str
    test_output: str
    test_passed: bool


@dataclass
class RefactorResult:
    """Result of the REFACTOR phase.

    Attributes:
        impl_path: Path to the refactored implementation.
        test_output: Output from running the test.
        test_passed: Whether tests still pass.
        reverted: Whether changes were reverted.
    """

    impl_path: str
    test_output: str
    test_passed: bool
    reverted: bool = False


@dataclass
class CycleResult:
    """Overall result of a TDD cycle.

    Attributes:
        state: Final state of the cycle.
        red_result: Result from RED phase.
        green_result: Result from GREEN phase.
        refactor_result: Result from REFACTOR phase (if run).
        retry_count: Number of GREEN phase retries.
        failure_reason: Reason for failure (if FAILED).
    """

    state: CycleState
    red_result: Optional[RedResult] = None
    green_result: Optional[GreenResult] = None
    refactor_result: Optional[RefactorResult] = None
    retry_count: int = 0
    failure_reason: Optional[str] = None


class TDDCycle:
    """TDD cycle state machine.

    Manages the Red/Green/Refactor flow with strict state transitions.
    Tracks history for debugging and reporting.

    Example:
        cycle = TDDCycle()
        cycle.start_red()
        # ... generate and run test ...
        cycle.complete_red(test_failed=True)
        # ... generate implementation ...
        cycle.complete_green(test_passed=True)
        cycle.skip_refactor()  # or complete_refactor()
    """

    def __init__(self) -> None:
        """Initialize TDDCycle in INIT state."""
        self._state = CycleState.INIT
        self._history: list[CycleState] = [CycleState.INIT]
        self._failure_reason: Optional[str] = None
        self._red_result: Optional[RedResult] = None
        self._green_result: Optional[GreenResult] = None
        self._refactor_result: Optional[RefactorResult] = None
        self._retry_count = 0

    @property
    def state(self) -> CycleState:
        """Current state of the cycle."""
        return self._state

    def _transition(self, new_state: CycleState) -> None:
        """Perform a state transition and record in history."""
        logger.info(f"TDDCycle: {self._state} -> {new_state}")
        self._state = new_state
        self._history.append(new_state)

    def _require_state(self, *allowed_states: CycleState) -> None:
        """Raise InvalidTransitionError if not in allowed state."""
        if self._state not in allowed_states:
            raise InvalidTransitionError(
                f"Cannot perform this action from state {self._state}. "
                f"Allowed states: {', '.join(s.value for s in allowed_states)}"
            )

    def start_red(self) -> None:
        """Start the RED phase (generate failing test).

        Raises:
            InvalidTransitionError: If not in INIT state.
        """
        self._require_state(CycleState.INIT)
        self._transition(CycleState.RED)

    def complete_red(self, test_failed: bool) -> None:
        """Complete the RED phase.

        Args:
            test_failed: Whether the generated test fails (expected: True).

        Raises:
            InvalidTransitionError: If not in RED state.
            InvalidTestError: If test_failed is False (test doesn't test anything).
        """
        self._require_state(CycleState.RED)

        if not test_failed:
            raise InvalidTestError(
                "Test passed in RED phase - the test doesn't test anything. "
                "A valid TDD test must fail before implementation exists."
            )

        self._transition(CycleState.GREEN)

    def complete_green(self, test_passed: bool) -> None:
        """Complete the GREEN phase.

        Args:
            test_passed: Whether the test now passes (expected: True).

        Raises:
            InvalidTransitionError: If not in GREEN state.
            NeedsRetryError: If test_passed is False (implementation failed).
        """
        self._require_state(CycleState.GREEN)

        if not test_passed:
            raise NeedsRetryError(
                "Test still fails in GREEN phase - implementation incomplete. "
                "Retry or escalate."
            )

        self._transition(CycleState.REFACTOR)

    def skip_refactor(self) -> None:
        """Skip the REFACTOR phase and go directly to DONE.

        Raises:
            InvalidTransitionError: If not in REFACTOR state.
        """
        self._require_state(CycleState.REFACTOR)
        self._transition(CycleState.DONE)

    def complete_refactor(self, test_passed: bool) -> None:
        """Complete the REFACTOR phase.

        Args:
            test_passed: Whether tests still pass after refactoring.

        Raises:
            InvalidTransitionError: If not in REFACTOR state.

        Note:
            If test_passed is False, changes should be reverted externally
            and this method still transitions to DONE (with refactor skipped).
        """
        self._require_state(CycleState.REFACTOR)
        self._transition(CycleState.DONE)

    def mark_failed(self, reason: str) -> None:
        """Mark the cycle as FAILED.

        Args:
            reason: Description of why the cycle failed.

        Note:
            Can be called from RED, GREEN, or REFACTOR states.
        """
        self._require_state(CycleState.RED, CycleState.GREEN, CycleState.REFACTOR)
        self._failure_reason = reason
        self._transition(CycleState.FAILED)

    def get_history(self) -> list[CycleState]:
        """Get the state transition history.

        Returns:
            List of states in order of transitions.
        """
        return self._history.copy()

    def get_result(self) -> CycleResult:
        """Get the overall cycle result.

        Returns:
            CycleResult with all phase results and metadata.
        """
        return CycleResult(
            state=self._state,
            red_result=self._red_result,
            green_result=self._green_result,
            refactor_result=self._refactor_result,
            retry_count=self._retry_count,
            failure_reason=self._failure_reason,
        )

    def set_red_result(self, result: RedResult) -> None:
        """Store the RED phase result."""
        self._red_result = result

    def set_green_result(self, result: GreenResult) -> None:
        """Store the GREEN phase result."""
        self._green_result = result

    def set_refactor_result(self, result: RefactorResult) -> None:
        """Store the REFACTOR phase result."""
        self._refactor_result = result

    def increment_retry(self) -> int:
        """Increment and return the retry count."""
        self._retry_count += 1
        return self._retry_count


class TDDCycleExecutor:
    """Executes TDD cycle phases with actual code generation.

    Handles:
    - Dispatching to ModelDispatcher for code generation (Flash)
    - Writing generated code to files
    - Running tests with PytestRunner
    - Extracting code from model responses

    Example:
        executor = TDDCycleExecutor(dispatcher, working_dir="/tmp/worktree")
        red_result = executor.execute_red("Test add function", "add.py")
        green_result = executor.execute_green(red_result)
    """

    def __init__(
        self,
        dispatcher: "ModelDispatcher",
        working_dir: str,
        pytest_runner: Optional["PytestRunner"] = None,
    ) -> None:
        """Initialize TDDCycleExecutor.

        Args:
            dispatcher: ModelDispatcher for sending requests to Flash.
            working_dir: Directory to write generated files.
            pytest_runner: PytestRunner instance (creates default if None).
        """
        self.dispatcher = dispatcher
        self.working_dir = Path(working_dir)
        self.working_dir.mkdir(parents=True, exist_ok=True)

        if pytest_runner is None:
            from orchestrator.pytest_runner import PytestRunner
            self.pytest_runner = PytestRunner()
        else:
            self.pytest_runner = pytest_runner

    def _extract_code(self, response: str) -> str:
        """Extract Python code from model response.

        Args:
            response: Raw model response potentially containing markdown.

        Returns:
            Extracted Python code.
        """
        # Try to extract from markdown code blocks
        code_pattern = r"```(?:python)?\n(.*?)```"
        matches = re.findall(code_pattern, response, re.DOTALL)
        if matches:
            return "\n\n".join(matches).strip()
        # Return raw response if no code blocks found
        return response.strip()

    def _derive_test_filename(self, target_file: str) -> str:
        """Derive test filename from target filename.

        Args:
            target_file: Implementation file name (e.g., "sum.py").

        Returns:
            Test filename (e.g., "test_sum.py").
        """
        base = Path(target_file).stem
        return f"test_{base}.py"

    def execute_red(
        self,
        task_description: str,
        target_file: str,
        test_filename: Optional[str] = None,
    ) -> RedResult:
        """Execute the RED phase: generate and verify a failing test.

        Args:
            task_description: Description of what to test.
            target_file: Target implementation file (for naming).
            test_filename: Optional override for test filename.

        Returns:
            RedResult with test path and output.

        Raises:
            DispatchError: If model dispatch fails.
            InvalidTestError: If generated test passes (invalid test).
        """
        logger.info(f"Executing RED phase for: {task_description}")

        # Dispatch to Flash for test generation
        prompt_vars = {
            "task_description": task_description,
            "target_file": target_file,
            "phase": "red",
        }

        dispatch_result = self.dispatcher.send_request("tdd_worker", prompt_vars)

        if not dispatch_result.success:
            raise DispatchError(
                f"Failed to generate test: {dispatch_result.error}"
            )

        # Extract and write test code
        test_code = self._extract_code(dispatch_result.response)
        test_file = test_filename or self._derive_test_filename(target_file)
        test_path = self.working_dir / test_file

        test_path.write_text(test_code)
        logger.info(f"Wrote test to: {test_path}")

        # Run the test - it should FAIL
        pytest_result = self.pytest_runner.run(str(test_path))

        from orchestrator.pytest_runner import TestStatus

        test_failed = pytest_result.status in (TestStatus.FAILED, TestStatus.ERROR)
        test_output = pytest_result.stdout + pytest_result.stderr

        if not test_failed:
            raise InvalidTestError(
                f"Test passed in RED phase - invalid test. "
                f"Test output: {test_output[:500]}"
            )

        # Validate test quality (prevent trivial/cheating tests)
        from orchestrator.validate_test import validate

        validation_result = validate(str(test_path), target_file)
        if not validation_result.valid:
            raise InvalidTestError(
                f"Test validation failed: {'; '.join(validation_result.errors)}"
            )

        return RedResult(
            test_path=str(test_path),
            test_output=test_output,
            test_failed=True,
        )

    def execute_green(
        self,
        red_result: RedResult,
        target_file: str,
        previous_error: Optional[str] = None,
    ) -> GreenResult:
        """Execute the GREEN phase: generate minimal implementation.

        Args:
            red_result: Result from RED phase with test path and output.
            target_file: Target implementation file.
            previous_error: Error from previous GREEN attempt (for retry).

        Returns:
            GreenResult with impl path and test output.

        Raises:
            DispatchError: If model dispatch fails.
            NeedsRetryError: If test still fails after implementation.
        """
        logger.info(f"Executing GREEN phase for: {target_file}")

        # Read the test file content
        test_content = Path(red_result.test_path).read_text()

        # Build prompt with test context
        prompt_vars = {
            "task_description": f"Implement minimal code to pass this test:\n\n{test_content}",
            "target_file": target_file,
            "phase": "green",
            "test_output": red_result.test_output,
        }

        if previous_error:
            prompt_vars["previous_error"] = previous_error

        dispatch_result = self.dispatcher.send_request("tdd_worker", prompt_vars)

        if not dispatch_result.success:
            raise DispatchError(
                f"Failed to generate implementation: {dispatch_result.error}"
            )

        # Extract and write implementation code
        impl_code = self._extract_code(dispatch_result.response)
        impl_path = self.working_dir / target_file

        impl_path.write_text(impl_code)
        logger.info(f"Wrote implementation to: {impl_path}")

        # Run the test - it should PASS
        pytest_result = self.pytest_runner.run(red_result.test_path)

        from orchestrator.pytest_runner import TestStatus

        test_passed = pytest_result.status == TestStatus.PASSED
        test_output = pytest_result.stdout + pytest_result.stderr

        if not test_passed:
            raise NeedsRetryError(
                f"Test still fails in GREEN phase. Output: {test_output[:500]}"
            )

        return GreenResult(
            impl_path=str(impl_path),
            test_output=test_output,
            test_passed=True,
        )

    def execute_refactor(
        self,
        green_result: GreenResult,
        test_path: str,
    ) -> RefactorResult:
        """Execute the REFACTOR phase: optional cleanup.

        Args:
            green_result: Result from GREEN phase.
            test_path: Path to the test file.

        Returns:
            RefactorResult with refactored code and test status.
        """
        logger.info(f"Executing REFACTOR phase for: {green_result.impl_path}")

        # Read current implementation
        impl_content = Path(green_result.impl_path).read_text()
        test_content = Path(test_path).read_text()

        # Dispatch for refactoring
        prompt_vars = {
            "task_description": f"Refactor this implementation while keeping tests passing:\n\n{impl_content}",
            "target_file": Path(green_result.impl_path).name,
            "phase": "refactor",
            "test_content": test_content,
        }

        dispatch_result = self.dispatcher.send_request("tdd_worker", prompt_vars)

        if not dispatch_result.success:
            # Refactor is optional - skip on failure
            logger.warning(f"Refactor dispatch failed: {dispatch_result.error}")
            return RefactorResult(
                impl_path=green_result.impl_path,
                test_output="Refactor skipped due to dispatch failure",
                test_passed=True,
                reverted=False,
            )

        # Save original for potential revert
        original_code = impl_content
        refactored_code = self._extract_code(dispatch_result.response)

        # Write refactored code
        impl_path = Path(green_result.impl_path)
        impl_path.write_text(refactored_code)

        # Run tests to verify
        pytest_result = self.pytest_runner.run(test_path)

        from orchestrator.pytest_runner import TestStatus

        test_passed = pytest_result.status == TestStatus.PASSED
        test_output = pytest_result.stdout + pytest_result.stderr

        if not test_passed:
            # Revert on test failure
            logger.warning("Refactor broke tests - reverting")
            impl_path.write_text(original_code)
            return RefactorResult(
                impl_path=str(impl_path),
                test_output=test_output,
                test_passed=False,
                reverted=True,
            )

        return RefactorResult(
            impl_path=str(impl_path),
            test_output=test_output,
            test_passed=True,
            reverted=False,
        )

    def execute_green_with_retry(
        self,
        red_result: RedResult,
        target_file: str,
        retry_policy: "RetryPolicy",
    ) -> GreenResult:
        """Execute GREEN phase with retry loop.

        Args:
            red_result: Result from RED phase.
            target_file: Target implementation file.
            retry_policy: RetryPolicy instance for managing retries.

        Returns:
            GreenResult on successful implementation.

        Raises:
            MaxRetriesExceeded: If all retry attempts fail.
            DispatchError: If model dispatch fails.
        """
        from orchestrator.retry_policy import RetryPolicy

        previous_error: Optional[str] = None

        while retry_policy.should_retry():
            try:
                result = self.execute_green(
                    red_result,
                    target_file,
                    previous_error=previous_error,
                )
                retry_policy.record_attempt(success=True)
                return result

            except NeedsRetryError as e:
                previous_error = str(e)
                retry_policy.record_attempt(success=False, error=previous_error)
                delay = retry_policy.get_backoff_delay()
                if delay > 0:
                    logger.info(f"Backing off for {delay:.1f}s before retry")
                    time.sleep(delay)
                logger.info(
                    f"GREEN phase retry {retry_policy.get_retry_count()}/{retry_policy.max_attempts}"
                )

        # Max retries exceeded
        raise MaxRetriesExceeded(
            retry_count=retry_policy.get_retry_count(),
            error_history=retry_policy.get_error_history(),
        )


class TDDFullCycleRunner:
    """Runs a complete TDD cycle within a worktree.

    Integrates:
    - WorktreeManager for isolation
    - TDDCycleExecutor for phase execution
    - TDDCycle state machine for transitions
    - RetryPolicy for self-repair

    Workflow:
    1. start_cycle() - creates worktree, initializes executor
    2. run_red_phase() - generates and validates failing test
    3. run_green_phase() - generates implementation with retry
    4. finish_cycle() - optional refactor, merge to main
    or abort_cycle() - cleanup on failure

    Example:
        runner = TDDFullCycleRunner(worktree_manager, dispatcher)
        runner.start_cycle(task_id="task_001", task_description="...", target_file="impl.py")
        runner.run_red_phase()
        runner.run_green_phase()
        runner.finish_cycle()
    """

    def __init__(
        self,
        worktree_manager: "WorktreeManager",
        dispatcher: "ModelDispatcher",
        pytest_runner: Optional["PytestRunner"] = None,
        retry_policy: Optional["RetryPolicy"] = None,
        queue_path: Optional[str] = None,
        northstar_path: Optional[str] = None,
    ) -> None:
        """Initialize TDDFullCycleRunner.

        Args:
            worktree_manager: WorktreeManager for isolation.
            dispatcher: ModelDispatcher for AI generation.
            pytest_runner: PytestRunner instance (creates default if None).
            retry_policy: RetryPolicy for GREEN phase retries.
            queue_path: Path to queue.json for DNA check.
            northstar_path: Path to NORTHSTAR.md for DNA check.
        """
        self.worktree_manager = worktree_manager
        self.dispatcher = dispatcher
        self.pytest_runner = pytest_runner
        self.retry_policy = retry_policy
        self.queue_path = queue_path
        self.northstar_path = northstar_path

        self._cycle: Optional[TDDCycle] = None
        self._executor: Optional[TDDCycleExecutor] = None
        self._task_id: Optional[str] = None
        self._task_description: Optional[str] = None
        self._target_file: Optional[str] = None
        self._worktree_path: Optional[str] = None
        self._red_result: Optional[RedResult] = None
        self._green_result: Optional[GreenResult] = None

    def start_cycle(
        self,
        task_id: str,
        task_description: str,
        target_file: str,
        attempt: int = 1,
    ) -> None:
        """Start a new TDD cycle.

        Creates worktree and initializes executor.

        Args:
            task_id: Unique task identifier.
            task_description: Description of what to implement.
            target_file: Target implementation file name.
            attempt: Attempt number for the worktree branch.
        """
        self._task_id = task_id
        self._target_file = target_file
        self._task_description = task_description

        # Create worktree
        self._worktree_path = self.worktree_manager.create(
            task_id=task_id,
            attempt=attempt,
        )

        # Initialize executor with worktree as working dir
        self._executor = TDDCycleExecutor(
            dispatcher=self.dispatcher,
            working_dir=self._worktree_path,
            pytest_runner=self.pytest_runner,
        )

        # Initialize state machine
        self._cycle = TDDCycle()
        self._cycle.start_red()

        logger.info(f"Started TDD cycle for task '{task_id}' in {self._worktree_path}")

    def run_red_phase(self) -> RedResult:
        """Run the RED phase: generate and validate failing test.

        Returns:
            RedResult with test path and output.

        Raises:
            RuntimeError: If start_cycle() was not called first.
            InvalidTestError: If generated test passes.
            DispatchError: If model dispatch fails.
        """
        if not self._executor or not self._cycle:
            raise RuntimeError("Must call start_cycle() first")
        if self._task_description is None:
            raise RuntimeError("Must call start_cycle() first")

        result = self._executor.execute_red(
            task_description=self._task_description,
            target_file=self._target_file,
        )

        self._red_result = result
        self._cycle.complete_red(test_failed=result.test_failed)

        logger.info(f"RED phase complete: {result.test_path}")
        return result

    def run_green_phase(self) -> GreenResult:
        """Run the GREEN phase: generate implementation with retry.

        Returns:
            GreenResult with implementation path.

        Raises:
            MaxRetriesExceeded: If all retry attempts fail.
            DispatchError: If model dispatch fails.
        """
        if not self._executor or not self._cycle or not self._red_result:
            raise RuntimeError("Must call run_red_phase() first")

        # Use provided policy or create default
        policy = self.retry_policy
        if policy is None:
            from orchestrator.retry_policy import RetryPolicy
            policy = RetryPolicy(max_attempts=5)

        result = self._executor.execute_green_with_retry(
            red_result=self._red_result,
            target_file=self._target_file,
            retry_policy=policy,
        )

        self._green_result = result
        self._cycle.complete_green(test_passed=result.test_passed)

        logger.info(f"GREEN phase complete: {result.impl_path}")
        return result

    def finish_cycle(
        self,
        skip_refactor: bool = False,
        target_branch: str = "main",
    ) -> CycleResult:
        """Finish the cycle: optional refactor, then merge.

        Args:
            skip_refactor: Whether to skip the REFACTOR phase.
            target_branch: Branch to merge into.

        Returns:
            CycleResult with all phase results.
        """
        if not self._executor or not self._cycle or not self._green_result:
            raise RuntimeError("Must call run_green_phase() first")

        refactor_result = None
        if not skip_refactor:
            refactor_result = self._executor.execute_refactor(
                green_result=self._green_result,
                test_path=self._red_result.test_path,
            )
            self._cycle.complete_refactor(test_passed=refactor_result.test_passed)
        else:
            self._cycle.skip_refactor()

        # Store results
        self._cycle.set_red_result(self._red_result)
        self._cycle.set_green_result(self._green_result)
        if refactor_result:
            self._cycle.set_refactor_result(refactor_result)

        # Merge to main with DNA check if configured
        merge_kwargs = {
            "task_id": self._task_id,
            "target_branch": target_branch,
        }
        if self.queue_path and self.northstar_path:
            merge_kwargs["dna_check"] = True
            merge_kwargs["queue_path"] = self.queue_path
            merge_kwargs["northstar_path"] = self.northstar_path

        merge_result = self.worktree_manager.merge(**merge_kwargs)

        if not merge_result.success:
            logger.warning(f"Merge failed: {merge_result.message}")

        logger.info(f"TDD cycle complete for task '{self._task_id}'")
        return self._cycle.get_result()

    def abort_cycle(self) -> None:
        """Abort the cycle and cleanup worktree.

        Call this on failure to clean up resources.
        """
        if self._task_id and self.worktree_manager:
            self.worktree_manager.cleanup(task_id=self._task_id)
            logger.info(f"Aborted TDD cycle for task '{self._task_id}'")

        self._cycle = None
        self._executor = None
        self._red_result = None
        self._green_result = None
