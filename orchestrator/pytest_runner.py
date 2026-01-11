"""Pytest execution wrapper for TDD cycle.

This module provides the PytestRunner class which wraps pytest execution
and captures output for the TDD execution loop.

The runner:
- Executes pytest on a given test file
- Captures stdout, stderr, and exit code
- Supports configurable timeouts to prevent hung tests
- Returns structured PytestResult dataclass
"""

import logging
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class TestStatus(str, Enum):
    """Test execution status."""

    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class PytestResult:
    """Result of a pytest execution.

    Attributes:
        status: Test execution status (PASSED, FAILED, ERROR, TIMEOUT).
        exit_code: pytest exit code.
        stdout: Captured stdout output.
        stderr: Captured stderr output.
        test_path: Path to the test file that was executed.
    """

    status: TestStatus
    exit_code: int
    stdout: str
    stderr: str
    test_path: str


class PytestRunner:
    """Wraps pytest execution with output capture and timeout support.

    Attributes:
        default_timeout: Default timeout in seconds for test execution.
    """

    def __init__(self, default_timeout: int = 60) -> None:
        """Initialize PytestRunner.

        Args:
            default_timeout: Default timeout in seconds (default: 60).
        """
        self.default_timeout = default_timeout

    def run(
        self,
        test_path: str,
        timeout: Optional[int] = None,
        working_dir: Optional[str] = None,
    ) -> PytestResult:
        """Execute pytest on a test file.

        Args:
            test_path: Path to the test file to execute.
            timeout: Timeout in seconds (uses default_timeout if None).
            working_dir: Working directory for pytest (uses test file dir if None).

        Returns:
            PytestResult with status, exit code, and captured output.
        """
        timeout = timeout if timeout is not None else self.default_timeout
        test_path_obj = Path(test_path)

        # Check if test file exists
        if not test_path_obj.exists():
            logger.warning(f"Test file not found: {test_path}")
            return PytestResult(
                status=TestStatus.ERROR,
                exit_code=2,
                stdout="",
                stderr=f"Test file not found: {test_path}",
                test_path=test_path,
            )

        # Determine working directory
        cwd = working_dir if working_dir else str(test_path_obj.parent)

        # Build pytest command
        cmd = [
            "python3",
            "-m",
            "pytest",
            str(test_path_obj),
            "-v",
            "--tb=short",
            "-s",  # Capture stdout
        ]

        logger.info(f"Running pytest on {test_path} with timeout={timeout}s")

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            # Determine status from exit code
            if result.returncode == 0:
                status = TestStatus.PASSED
            elif result.returncode == 1:
                status = TestStatus.FAILED
            else:
                # Exit code 2 = user interrupt, 3 = internal error, etc.
                status = TestStatus.ERROR

            logger.info(f"Pytest completed with status={status}, exit_code={result.returncode}")

            return PytestResult(
                status=status,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                test_path=test_path,
            )

        except subprocess.TimeoutExpired:
            # Note: subprocess.run() with timeout internally kills the process
            # before raising TimeoutExpired, so no explicit cleanup needed.
            # This is documented behavior in Python's subprocess module.
            logger.warning(f"Pytest timed out after {timeout}s on {test_path}")
            return PytestResult(
                status=TestStatus.TIMEOUT,
                exit_code=-1,
                stdout="",
                stderr=f"Test execution timed out after {timeout} seconds",
                test_path=test_path,
            )

        except Exception as e:
            logger.error(f"Unexpected error running pytest: {e}")
            return PytestResult(
                status=TestStatus.ERROR,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                test_path=test_path,
            )
