"""Disk space checker for pre-flight safety validation.

This module implements disk space checking as part of the Resource Safety
protocol defined in CLAUDE.md. Before creating worktrees or performing
other disk-intensive operations, we must verify sufficient space exists.

CRITICAL SAFETY: Per CLAUDE.md Resource Safety rules, operations should
fail if disk usage exceeds 80% to prevent system instability.
"""

import shutil
from pathlib import Path


class DiskSpaceError(Exception):
    """Raised when disk space usage exceeds the safety threshold.

    Attributes:
        current_usage: Current disk usage percentage (0-100).
        threshold: Maximum allowed usage percentage.
    """

    def __init__(self, current_usage: float, threshold: float) -> None:
        self.current_usage = current_usage
        self.threshold = threshold
        super().__init__(
            f"Disk usage {current_usage:.1f}% exceeds threshold {threshold:.1f}%. "
            f"Free up disk space before proceeding."
        )


def check_disk_space(path: str, threshold: float = 80.0) -> float:
    """Check disk space usage on the filesystem containing the given path.

    Args:
        path: Path to check disk space for (uses the filesystem containing this path).
        threshold: Maximum allowed disk usage percentage (default: 80%).
            If usage exceeds this threshold, DiskSpaceError is raised.

    Returns:
        Current disk usage as a percentage (0-100).

    Raises:
        DiskSpaceError: If disk usage exceeds the threshold.
        OSError: If the path is invalid or inaccessible.
    """
    usage = shutil.disk_usage(path)
    usage_percent = (usage.used / usage.total) * 100

    if usage_percent > threshold:
        raise DiskSpaceError(current_usage=usage_percent, threshold=threshold)

    return usage_percent
