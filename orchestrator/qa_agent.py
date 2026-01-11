"""QA Agent module for H-Conductor quality gate.

This module implements the QAAgent class that performs code review
before merge. It integrates with the ModelDispatcher to route reviews
to the Pro model and with DNA check for NorthStar traceability.

QA Agent: Goal 1 - "Python Orchestrator (quality gates)"
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from orchestrator.dispatcher import ModelDispatcher
import re


class ReviewCategory(Enum):
    """Categories for code review issues."""

    LOGIC = "LOGIC"
    SECURITY = "SECURITY"
    STYLE = "STYLE"
    PERFORMANCE = "PERFORMANCE"
    REGRESSION = "REGRESSION"


@dataclass(frozen=True)
class ReviewIssue:
    """A single issue found during code review.

    Attributes:
        severity: Issue severity - 'critical', 'major', or 'minor'.
        category: Category of the issue (ReviewCategory enum).
        description: Description of the issue.
        location: Optional location in code (e.g., 'line 42').
    """

    severity: str  # 'critical', 'major', 'minor'
    category: ReviewCategory
    description: str
    location: Optional[str] = None


@dataclass(frozen=True)
class ReviewResult:
    """Result of a QA code review.

    Attributes:
        decision: Review decision - 'APPROVED', 'REJECTED', or 'NEEDS_REFINEMENT'.
        summary: One-line summary of the review.
        issues: List of issues found during review.
        recommendations: List of improvement suggestions.
        passed_checks: List of checks that passed.
    """

    decision: str  # 'APPROVED', 'REJECTED', 'NEEDS_REFINEMENT'
    summary: str
    issues: list[ReviewIssue] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    passed_checks: list[str] = field(default_factory=list)


class QAAgent:
    """Quality assurance agent for code review.

    Routes code reviews to Pro model via ModelDispatcher and integrates
    with DNA check for NorthStar traceability validation.

    Example:
        dispatcher = ModelDispatcher()
        agent = QAAgent(dispatcher)
        result = agent.review(task, code, test_results)
    """

    def __init__(self, dispatcher: "ModelDispatcher") -> None:
        """Initialize QAAgent with a model dispatcher.

        Args:
            dispatcher: ModelDispatcher instance for routing requests.
        """
        self.dispatcher = dispatcher

    def review(
        self,
        task: dict,
        code: str,
        test_results: str,
        existing_test_results: Optional[str] = None,
    ) -> ReviewResult:
        """Review code for quality, security, and logic issues.

        Args:
            task: Task dict with 'description' and optional 'security_boundaries'.
            code: The code to review.
            test_results: Results of tests for the new code.
            existing_test_results: Optional results from existing test suite.

        Returns:
            ReviewResult with decision, issues, and recommendations.
        """
        # Format task description with security boundaries if present
        task_description = self._format_task_description(task)

        # Include existing test results in context if provided
        full_test_results = test_results
        if existing_test_results:
            full_test_results = f"New Tests:\n{test_results}\n\nExisting Tests:\n{existing_test_results}"

        # Build prompt variables
        prompt_vars = {
            "code": code,
            "test_results": full_test_results,
            "task_description": task_description,
        }

        # Call dispatcher
        dispatch_result = self.dispatcher.send_request("qa_review", prompt_vars)

        if not dispatch_result.success:
            return ReviewResult(
                decision="NEEDS_REFINEMENT",
                summary=f"Review failed: {dispatch_result.error}",
                issues=[],
                recommendations=["Retry the review"],
                passed_checks=[],
            )

        # Parse the response
        return self._parse_review_response(dispatch_result.response, existing_test_results)

    def review_with_dna(
        self,
        task_id: str,
        queue_path: str,
        northstar_path: str,
        code: str,
        test_results: str,
        existing_test_results: Optional[str] = None,
    ) -> ReviewResult:
        """Review code and verify DNA traceability.

        Both code review and DNA check must pass for approval.

        Args:
            task_id: Task ID to check.
            queue_path: Path to queue.json file.
            northstar_path: Path to NORTHSTAR.md file.
            code: The code to review.
            test_results: Test results.
            existing_test_results: Optional existing test results.

        Returns:
            ReviewResult combining code review and DNA check.
        """
        # Import here to avoid circular dependency
        from orchestrator.dna_check import check_task_before_merge

        # First do code review
        # We need task info for code review - construct minimal task
        code_result = self.review(
            task={"description": f"Task {task_id}"},
            code=code,
            test_results=test_results,
            existing_test_results=existing_test_results,
        )

        # If code review failed, return immediately
        if code_result.decision == "REJECTED":
            return code_result

        # Run DNA check
        dna_result = check_task_before_merge(task_id, queue_path, northstar_path)

        if not dna_result.approved:
            # DNA check failed - override approval
            return ReviewResult(
                decision="REJECTED",
                summary=f"DNA drift detected: {dna_result.reason}",
                issues=list(code_result.issues),
                recommendations=list(code_result.recommendations) + [
                    "Ensure task traces to a NorthStar goal"
                ],
                passed_checks=list(code_result.passed_checks),
            )

        # Both passed
        return ReviewResult(
            decision="APPROVED",
            summary=f"{code_result.summary} DNA check passed.",
            issues=list(code_result.issues),
            recommendations=list(code_result.recommendations),
            passed_checks=list(code_result.passed_checks) + ["dna_traceability"],
        )

    def _format_task_description(self, task: dict) -> str:
        """Format task description including security boundaries."""
        description = task.get("description", "No description")

        security_boundaries = task.get("security_boundaries", [])
        if security_boundaries:
            boundaries_text = "\n".join(f"- {b}" for b in security_boundaries)
            description = f"{description}\n\nSecurity Boundaries:\n{boundaries_text}"

        return description

    def _parse_review_response(
        self, response: str, existing_test_results: Optional[str] = None
    ) -> ReviewResult:
        """Parse Pro model response into ReviewResult.

        Args:
            response: Raw response from Pro model.
            existing_test_results: Existing test results to check for regressions.

        Returns:
            Parsed ReviewResult.
        """
        # Extract decision
        decision = self._extract_decision(response)

        # Extract summary
        summary = self._extract_summary(response)

        # Extract issues
        issues = self._extract_issues(response)

        # Extract recommendations
        recommendations = self._extract_recommendations(response)

        # Check for critical security issues - override decision
        has_critical_security = any(
            i.severity == "critical" and i.category == ReviewCategory.SECURITY
            for i in issues
        )

        # Check for regression issues
        has_regression = any(i.category == ReviewCategory.REGRESSION for i in issues)

        # Also check if existing tests show failures (not just "0 failed")
        if existing_test_results and self._has_test_failures(existing_test_results):
            # Check if we already have a regression issue
            if not has_regression:
                issues = list(issues) + [
                    ReviewIssue(
                        severity="critical",
                        category=ReviewCategory.REGRESSION,
                        description="Existing tests are failing",
                    )
                ]
                has_regression = True

        # Override APPROVED if critical issues found
        if decision == "APPROVED" and (has_critical_security or has_regression):
            decision = "REJECTED"
            if has_critical_security:
                summary = f"Rejected due to critical security issue. {summary}"
            elif has_regression:
                summary = f"Rejected due to regression. {summary}"

        # Determine passed checks
        passed_checks = []
        if not any(i.category == ReviewCategory.LOGIC for i in issues if i.severity == "critical"):
            passed_checks.append("logic")
        if not has_critical_security:
            passed_checks.append("security")
        if not has_regression:
            passed_checks.append("regression")

        return ReviewResult(
            decision=decision,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            passed_checks=passed_checks,
        )

    def _extract_decision(self, response: str) -> str:
        """Extract decision from response."""
        upper = response.upper()
        if "REJECTED" in upper:
            return "REJECTED"
        elif "NEEDS_REFINEMENT" in upper:
            return "NEEDS_REFINEMENT"
        elif "APPROVED" in upper:
            return "APPROVED"
        return "NEEDS_REFINEMENT"

    def _extract_summary(self, response: str) -> str:
        """Extract summary from response."""
        # Look for ## Summary section
        summary_match = re.search(
            r"##\s*Summary\s*\n(.+?)(?=\n##|\Z)", response, re.DOTALL | re.IGNORECASE
        )
        if summary_match:
            return summary_match.group(1).strip().split("\n")[0]

        # Fallback: first non-header line
        lines = [l.strip() for l in response.split("\n") if l.strip() and not l.startswith("#")]
        return lines[0] if lines else "Review complete"

    def _extract_issues(self, response: str) -> list[ReviewIssue]:
        """Extract issues from response."""
        issues = []

        # Pattern: - [severity] CATEGORY: description (location)
        issue_pattern = re.compile(
            r"-\s*\[(\w+)\]\s*(\w+):\s*(.+?)(?:\s*\(([^)]+)\))?$",
            re.MULTILINE,
        )

        for match in issue_pattern.finditer(response):
            severity = match.group(1).lower()
            category_str = match.group(2).upper()
            description = match.group(3).strip()
            location = match.group(4)

            # Map category string to enum
            try:
                category = ReviewCategory[category_str]
            except KeyError:
                category = ReviewCategory.LOGIC  # Default

            issues.append(
                ReviewIssue(
                    severity=severity,
                    category=category,
                    description=description,
                    location=location,
                )
            )

        return issues

    def _extract_recommendations(self, response: str) -> list[str]:
        """Extract recommendations from response."""
        recommendations = []

        # Look for ## Recommendations section
        rec_match = re.search(
            r"##\s*Recommendations?\s*\n(.+?)(?=\n##|\Z)", response, re.DOTALL | re.IGNORECASE
        )
        if rec_match:
            rec_text = rec_match.group(1)
            # Extract bullet points
            for line in rec_text.split("\n"):
                line = line.strip()
                if line.startswith("-"):
                    recommendations.append(line[1:].strip())

        return recommendations

    def _has_test_failures(self, test_results: str) -> bool:
        """Check if test results indicate actual failures.

        Args:
            test_results: Test output string.

        Returns:
            True if there are actual test failures, False otherwise.
        """
        # Check for pytest-style "FAILED:" marker
        if "FAILED:" in test_results or "FAILED " in test_results:
            return True

        # Check for "N failed" where N > 0
        failed_match = re.search(r"(\d+)\s+failed", test_results, re.IGNORECASE)
        if failed_match:
            failed_count = int(failed_match.group(1))
            if failed_count > 0:
                return True

        # Check for "failures" in error output
        if re.search(r"\b(?:error|failure|exception)\b", test_results, re.IGNORECASE):
            # But not if it says "0 errors" or "0 failures"
            if re.search(r"\b0\s+(?:errors?|failures?)\b", test_results, re.IGNORECASE):
                return False
            return True

        return False


def format_feedback(result: ReviewResult) -> str:
    """Format ReviewResult as human-readable markdown feedback.

    Args:
        result: The review result to format.

    Returns:
        Markdown-formatted feedback string.
    """
    lines = [
        f"# QA Review Feedback",
        f"",
        f"**Decision:** {result.decision}",
        f"",
        f"**Summary:** {result.summary}",
        f"",
    ]

    if result.issues:
        lines.append("## Issues")
        lines.append("")
        for issue in result.issues:
            location_str = f" ({issue.location})" if issue.location else ""
            lines.append(f"- **[{issue.severity}]** {issue.category.value}: {issue.description}{location_str}")
        lines.append("")

    if result.recommendations:
        lines.append("## Recommendations")
        lines.append("")
        for rec in result.recommendations:
            lines.append(f"- {rec}")
        lines.append("")

    if result.passed_checks:
        lines.append("## Passed Checks")
        lines.append("")
        for check in result.passed_checks:
            lines.append(f"- {check}")
        lines.append("")

    return "\n".join(lines)


def save_feedback(task_id: str, result: ReviewResult, output_path: str) -> None:
    """Save review feedback to a file.

    Args:
        task_id: The task ID being reviewed.
        result: The review result.
        output_path: Path to save the feedback file.
    """
    feedback = format_feedback(result)

    # Add header with task ID and timestamp
    timestamp = datetime.now().isoformat()
    header = f"# Review for {task_id}\n\n**Timestamp:** {timestamp}\n\n---\n\n"

    full_content = header + feedback

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(full_content)
