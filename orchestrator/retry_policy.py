"""Retry policy for TDD cycle self-repair loop.

This module provides the RetryPolicy class which manages retry attempts
for the GREEN phase of TDD execution.

Features:
- Configurable max attempts (default: 5)
- Error history tracking for debugging
- Exponential backoff between retries
- Success/completion tracking
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class RetryPolicy:
    """Manages retry attempts with configurable limits.

    Provides:
    - Max attempt tracking
    - Error history
    - Exponential backoff
    - Reset capability

    Example:
        policy = RetryPolicy(max_attempts=5)
        while policy.should_retry():
            try:
                result = execute_green_phase()
                policy.record_attempt(success=True)
                break
            except NeedsRetryError as e:
                policy.record_attempt(success=False, error=str(e))
                time.sleep(policy.get_backoff_delay())
    """

    def __init__(
        self,
        max_attempts: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
    ) -> None:
        """Initialize RetryPolicy.

        Args:
            max_attempts: Maximum number of retry attempts (default: 5).
            base_delay: Base delay for exponential backoff in seconds.
            max_delay: Maximum delay cap for backoff in seconds.
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay

        self._attempt_count = 0
        self._error_history: list[str] = []
        self._is_complete = False

    @property
    def is_complete(self) -> bool:
        """Whether the operation completed successfully."""
        return self._is_complete

    @property
    def last_error(self) -> Optional[str]:
        """Get the most recent error, if any."""
        return self._error_history[-1] if self._error_history else None

    def should_retry(self) -> bool:
        """Check if another retry attempt should be made.

        Returns:
            True if more attempts are allowed and not yet complete.
        """
        if self._is_complete:
            return False
        return self._attempt_count < self.max_attempts

    def record_attempt(
        self,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        """Record an attempt result.

        Args:
            success: Whether the attempt succeeded.
            error: Error message if failed (optional).
        """
        self._attempt_count += 1

        if success:
            self._is_complete = True
            logger.info(f"Attempt {self._attempt_count} succeeded")
        else:
            if error:
                self._error_history.append(error)
            logger.info(
                f"Attempt {self._attempt_count}/{self.max_attempts} failed: {error}"
            )

    def get_retry_count(self) -> int:
        """Get the current retry count.

        Returns:
            Number of attempts made so far.
        """
        return self._attempt_count

    def get_error_history(self) -> list[str]:
        """Get all recorded errors.

        Returns:
            List of error messages from failed attempts.
        """
        return self._error_history.copy()

    def get_backoff_delay(self) -> float:
        """Get the delay before the next retry using exponential backoff.

        Returns:
            Delay in seconds (0 for first attempt).
        """
        if self._attempt_count == 0:
            return 0

        # Exponential backoff: base_delay * 2^(attempt-1)
        delay = self.base_delay * (2 ** (self._attempt_count - 1))
        return min(delay, self.max_delay)

    def reset(self) -> None:
        """Reset the policy to initial state.

        Clears attempt count, error history, and completion status.
        """
        self._attempt_count = 0
        self._error_history = []
        self._is_complete = False
        logger.info("RetryPolicy reset")
