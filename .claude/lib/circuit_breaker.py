"""Circuit breaker implementation for loop protection."""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class CircuitBreaker:
    """Circuit breaker for protecting against infinite retry loops."""

    loop_name: str
    max_retries: int
    current_retries: int = 0

    def can_retry(self) -> bool:
        """Check if another retry is allowed."""
        return self.current_retries < self.max_retries

    def record_failure(self) -> None:
        """Record a failure attempt."""
        self.current_retries += 1

    def reset(self) -> None:
        """Reset the breaker to initial state."""
        self.current_retries = 0

    def is_tripped(self) -> bool:
        """Check if the breaker has tripped (max retries exceeded)."""
        return self.current_retries >= self.max_retries


CIRCUIT_LIMITS: Dict[str, int] = {
    'plan': 5,
    'qa_write': 5,
    'qa_critic': 5,
    'dev': 20,  # 20 workers, 2 attempts each = 40 attempts total
    'review': 3
}


def get_breaker(loop_name: str, max_retries: Optional[int] = None) -> CircuitBreaker:
    """Factory function to create a circuit breaker.

    Args:
        loop_name: Name of the loop/phase this breaker protects
        max_retries: Override for max retries. If None, uses CIRCUIT_LIMITS or defaults to 3.

    Returns:
        A new CircuitBreaker instance
    """
    if max_retries is None:
        max_retries = CIRCUIT_LIMITS.get(loop_name, 3)
    return CircuitBreaker(loop_name=loop_name, max_retries=max_retries)


class CircuitBreakerManager:
    """Manager for multiple circuit breakers across different loops."""

    def __init__(self) -> None:
        self._breakers: Dict[str, CircuitBreaker] = {}

    def get(self, loop_name: str, max_retries: Optional[int] = None) -> CircuitBreaker:
        """Get or create a circuit breaker for the given loop.

        Args:
            loop_name: Name of the loop/phase
            max_retries: Override for max retries

        Returns:
            The circuit breaker for this loop
        """
        if loop_name not in self._breakers:
            self._breakers[loop_name] = get_breaker(loop_name, max_retries)
        return self._breakers[loop_name]

    def reset(self, loop_name: str) -> None:
        """Reset a specific breaker."""
        if loop_name in self._breakers:
            self._breakers[loop_name].reset()

    def reset_all(self) -> None:
        """Reset all breakers."""
        for breaker in self._breakers.values():
            breaker.reset()

    def is_any_tripped(self) -> bool:
        """Check if any breaker is tripped."""
        return any(b.is_tripped() for b in self._breakers.values())

    def get_tripped(self) -> list[str]:
        """Get list of tripped breaker names."""
        return [name for name, b in self._breakers.items() if b.is_tripped()]

    def status(self) -> Dict[str, Dict[str, int]]:
        """Get status of all breakers."""
        return {
            name: {
                'current': b.current_retries,
                'max': b.max_retries,
                'remaining': b.max_retries - b.current_retries
            }
            for name, b in self._breakers.items()
        }
