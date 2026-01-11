"""Escalation policy for blocked tasks.

This module provides the EscalationPolicy class for handling tasks
that have exceeded max retries and cannot be automatically fixed.

Features:
- Structured escalation with diagnostic info
- Optional Pro model diagnosis
- Callback support for custom handling
- Recommendations based on error patterns
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from orchestrator.dispatcher import ModelDispatcher

logger = logging.getLogger(__name__)


@dataclass
class EscalationResult:
    """Result of an escalation event.

    Attributes:
        task_id: ID of the blocked task.
        escalated: Whether escalation was triggered.
        error_history: List of errors from retry attempts.
        last_output: Final test/execution output.
        timestamp: When escalation occurred.
        diagnosis: Optional diagnosis from Pro model.
        recommendations: Suggested actions.
        summary: Human-readable summary message.
    """

    task_id: str
    escalated: bool
    error_history: list[str]
    last_output: str
    timestamp: datetime
    diagnosis: Optional[str] = None
    recommendations: list[str] = field(default_factory=list)
    summary: str = ""


class EscalationPolicy:
    """Handles blocked tasks that exceed max retries.

    Provides:
    - Diagnostic information capture
    - Optional Pro model analysis
    - Custom callback support
    - Structured recommendations

    Example:
        policy = EscalationPolicy()
        result = policy.on_blocked(
            task_id="task_001",
            error_history=["Error 1", "Error 2"],
            last_output="test output",
        )
        print(result.summary)
    """

    def __init__(
        self,
        dispatcher: Optional["ModelDispatcher"] = None,
        enable_pro_diagnosis: bool = False,
        on_escalation_callback: Optional[Callable[[EscalationResult], None]] = None,
    ) -> None:
        """Initialize EscalationPolicy.

        Args:
            dispatcher: ModelDispatcher for Pro diagnosis (optional).
            enable_pro_diagnosis: Whether to request Pro model analysis.
            on_escalation_callback: Callback function for escalation events.
        """
        self.dispatcher = dispatcher
        self.enable_pro_diagnosis = enable_pro_diagnosis
        self.on_escalation_callback = on_escalation_callback

    def on_blocked(
        self,
        task_id: str,
        error_history: list[str],
        last_output: str,
    ) -> EscalationResult:
        """Handle a blocked task.

        Args:
            task_id: ID of the blocked task.
            error_history: List of errors from retry attempts.
            last_output: Final test/execution output.

        Returns:
            EscalationResult with diagnostic information.
        """
        timestamp = datetime.now()

        logger.warning(
            f"Task '{task_id}' escalated after {len(error_history)} failed attempts"
        )

        # Generate recommendations based on error patterns
        recommendations = self._generate_recommendations(error_history, last_output)

        # Optional Pro diagnosis
        diagnosis = None
        if self.enable_pro_diagnosis and self.dispatcher:
            diagnosis = self._get_pro_diagnosis(error_history, last_output)

        # Generate summary
        summary = self._generate_summary(task_id, error_history, recommendations)

        result = EscalationResult(
            task_id=task_id,
            escalated=True,
            error_history=error_history,
            last_output=last_output,
            timestamp=timestamp,
            diagnosis=diagnosis,
            recommendations=recommendations,
            summary=summary,
        )

        # Call callback if provided
        if self.on_escalation_callback:
            self.on_escalation_callback(result)

        return result

    def _generate_recommendations(
        self,
        error_history: list[str],
        last_output: str,
    ) -> list[str]:
        """Generate recommendations based on error patterns.

        Args:
            error_history: List of errors.
            last_output: Final output.

        Returns:
            List of recommendation strings.
        """
        recommendations = []
        combined = " ".join(error_history) + " " + last_output

        # Check for common error patterns
        if "ImportError" in combined or "ModuleNotFoundError" in combined:
            recommendations.append(
                "Check if required dependencies are installed in the worktree"
            )
            recommendations.append("Verify import statements match actual module paths")

        if "TypeError" in combined:
            recommendations.append("Review type annotations and function signatures")
            recommendations.append("Check for mismatched argument types")

        if "AssertionError" in combined:
            recommendations.append("Review test assertions and expected values")
            recommendations.append("Check if implementation logic is correct")

        if "AttributeError" in combined:
            recommendations.append("Verify object attributes and method names")
            recommendations.append("Check for typos in attribute access")

        if "SyntaxError" in combined:
            recommendations.append("Check generated code for syntax errors")
            recommendations.append("Review code formatting and indentation")

        # Default recommendation if no patterns matched
        if not recommendations:
            recommendations.append("Review the error history for patterns")
            recommendations.append("Consider simplifying the task description")
            recommendations.append("Try breaking the task into smaller subtasks")

        return recommendations

    def _get_pro_diagnosis(
        self,
        error_history: list[str],
        last_output: str,
    ) -> Optional[str]:
        """Request Pro model diagnosis.

        Args:
            error_history: List of errors.
            last_output: Final output.

        Returns:
            Diagnosis string or None if unavailable.
        """
        if not self.dispatcher:
            return None

        # Build diagnostic prompt
        prompt_vars = {
            "task_description": f"""Analyze these TDD execution errors and provide a diagnosis:

Error History:
{chr(10).join(f'- {e}' for e in error_history)}

Last Output:
{last_output}

Provide a brief analysis of what's going wrong and potential root causes.""",
            "target_file": "diagnosis",
            "phase": "qa_review",
        }

        try:
            result = self.dispatcher.send_request("qa_review", prompt_vars)
            if result.success:
                return result.response
        except Exception as e:
            logger.warning(f"Pro diagnosis failed: {e}")

        return None

    def _generate_summary(
        self,
        task_id: str,
        error_history: list[str],
        recommendations: list[str],
    ) -> str:
        """Generate human-readable summary.

        Args:
            task_id: Task ID.
            error_history: List of errors.
            recommendations: List of recommendations.

        Returns:
            Summary string.
        """
        parts = [
            f"Task '{task_id}' blocked after {len(error_history)} failed attempts.",
            "",
            "Last error: " + (error_history[-1] if error_history else "Unknown"),
            "",
            "Recommendations:",
        ]
        parts.extend(f"  - {r}" for r in recommendations[:3])

        return "\n".join(parts)
