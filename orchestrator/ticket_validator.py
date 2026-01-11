"""Ticket validator for H-Conductor pre-execution review.

Performs lightweight 3-dimension validation (Clarity, Feasibility, Testability)
on tickets before TDD execution to catch obvious issues early.

Uses Flash proxy for fast, cost-effective validation.
"""

import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx

from orchestrator.config import get_proxy_config
from orchestrator.models import TaskModel, QueueModel


class TicketValidationError(Exception):
    """Raised when ticket validation fails unexpectedly."""

    pass


@dataclass
class ValidationIssue:
    """A single validation issue found in a ticket.

    Attributes:
        dimension: One of CLARITY, FEASIBILITY, TESTABILITY.
        issue: Brief description of the problem.
        severity: One of HIGH, MED, LOW.
    """

    dimension: str
    issue: str
    severity: str

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary for serialization."""
        return {
            "dimension": self.dimension,
            "issue": self.issue,
            "severity": self.severity,
        }


@dataclass
class TicketValidationResult:
    """Result of validating a single ticket.

    Attributes:
        ticket_id: ID of the validated ticket.
        issues: List of validation issues found.
        high_count: Number of HIGH severity issues.
        med_count: Number of MED severity issues.
        low_count: Number of LOW severity issues.
        proceed: Whether execution should proceed (false if high_count > 0).
        error: Error message if validation failed, None otherwise.
        latency_ms: Validation time in milliseconds.
    """

    ticket_id: str
    issues: list[ValidationIssue] = field(default_factory=list)
    high_count: int = 0
    med_count: int = 0
    low_count: int = 0
    proceed: bool = True
    error: Optional[str] = None
    latency_ms: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "ticket_id": self.ticket_id,
            "issues": [i.to_dict() for i in self.issues],
            "high_count": self.high_count,
            "med_count": self.med_count,
            "low_count": self.low_count,
            "proceed": self.proceed,
            "error": self.error,
            "latency_ms": self.latency_ms,
        }


@dataclass
class BatchValidationResult:
    """Result of validating multiple tickets.

    Attributes:
        results: List of individual validation results.
        total_count: Total tickets validated.
        proceed_count: Tickets that can proceed.
        blocked_count: Tickets blocked by HIGH issues.
        error_count: Tickets that failed validation.
    """

    results: list[TicketValidationResult] = field(default_factory=list)
    total_count: int = 0
    proceed_count: int = 0
    blocked_count: int = 0
    error_count: int = 0

    @property
    def summary(self) -> str:
        """Human-readable summary of batch validation."""
        return (
            f"Validated {self.total_count} tickets: "
            f"{self.proceed_count} proceed, "
            f"{self.blocked_count} blocked, "
            f"{self.error_count} errors"
        )


# Template path relative to orchestrator package
TEMPLATE_PATH = Path(__file__).parent / "framework/prompts/think-tank/ticket_validator.md"


def _load_template() -> str:
    """Load the ticket validator prompt template.

    Returns:
        Template content with placeholders.

    Raises:
        TicketValidationError: If template file not found.
    """
    if not TEMPLATE_PATH.exists():
        raise TicketValidationError(
            f"Ticket validator template not found: {TEMPLATE_PATH}"
        )
    return TEMPLATE_PATH.read_text()


def _parse_yaml_response(raw_response: str) -> dict:
    """Parse YAML-formatted validation response.

    Args:
        raw_response: Raw model response containing YAML.

    Returns:
        Parsed validation data.

    Raises:
        TicketValidationError: If YAML cannot be parsed.
    """
    # Extract YAML block from markdown if present
    yaml_pattern = r"```ya?ml\n(.*?)```"
    matches = re.findall(yaml_pattern, raw_response, re.DOTALL)

    yaml_content = matches[0] if matches else raw_response

    # Simple YAML parsing (avoid full yaml dependency for this structure)
    # Expected format is well-defined, so we parse manually
    try:
        result = {}

        # Extract ticket_id
        id_match = re.search(r"ticket_id:\s*[\"']?([^\"'\n]+)[\"']?", yaml_content)
        if id_match:
            result["ticket_id"] = id_match.group(1).strip()

        # Extract issues array
        issues = []
        # Match issue blocks - looking for dimension/issue/severity groups
        issue_pattern = r"-\s*dimension:\s*(\w+)\s+issue:\s*[\"']?([^\"'\n]+)[\"']?\s+severity:\s*(\w+)"
        issue_matches = re.findall(issue_pattern, yaml_content, re.MULTILINE)
        for dim, desc, sev in issue_matches:
            issues.append({
                "dimension": dim.upper(),
                "issue": desc.strip(),
                "severity": sev.upper(),
            })
        result["issues"] = issues

        # Extract summary counts
        high_match = re.search(r"high_count:\s*(\d+)", yaml_content)
        med_match = re.search(r"med_count:\s*(\d+)", yaml_content)
        low_match = re.search(r"low_count:\s*(\d+)", yaml_content)
        proceed_match = re.search(r"proceed:\s*(true|false)", yaml_content, re.IGNORECASE)

        result["high_count"] = int(high_match.group(1)) if high_match else 0
        result["med_count"] = int(med_match.group(1)) if med_match else 0
        result["low_count"] = int(low_match.group(1)) if low_match else 0
        result["proceed"] = proceed_match.group(1).lower() == "true" if proceed_match else True

        return result

    except Exception as e:
        raise TicketValidationError(f"Failed to parse validation response: {e}")


class TicketValidator:
    """Validates tickets using Flash proxy before TDD execution.

    Performs lightweight 3-dimension validation:
    - CLARITY: Is the ticket self-contained?
    - FEASIBILITY: Can this be done in isolation?
    - TESTABILITY: Can success be verified?

    Example:
        validator = TicketValidator()
        result = validator.validate_ticket(task)
        if result.proceed:
            # Execute task
        else:
            # Handle validation issues
    """

    def __init__(self, timeout: float = 30.0):
        """Initialize the validator.

        Args:
            timeout: Request timeout in seconds.
        """
        self.timeout = timeout
        self._template: Optional[str] = None

    @property
    def template(self) -> str:
        """Lazy-load the prompt template."""
        if self._template is None:
            self._template = _load_template()
        return self._template

    def _task_to_json(self, task: TaskModel) -> str:
        """Convert TaskModel to JSON for the prompt.

        Args:
            task: TaskModel to convert.

        Returns:
            JSON string representation.
        """
        return json.dumps({
            "id": task.id,
            "description": task.description,
            "status": task.status.value,
            "priority": task.priority,
            "northstar_goal": task.northstar_goal,
            "dependencies": task.dependencies,
            "success_definition": task.success_definition,
            "files": task.files,
            "source_file": task.source_file,
        }, indent=2)

    def _build_prompt(self, task: TaskModel) -> str:
        """Build the validation prompt for a task.

        Args:
            task: TaskModel to validate.

        Returns:
            Formatted prompt string.
        """
        ticket_json = self._task_to_json(task)
        # Replace template variables
        prompt = self.template.replace("{{TICKET_JSON}}", ticket_json)
        prompt = prompt.replace("{{OUTPUT_PATH}}", "stdout")  # We capture response directly
        return prompt

    def validate_ticket(self, task: TaskModel) -> TicketValidationResult:
        """Validate a single ticket.

        Args:
            task: TaskModel to validate.

        Returns:
            TicketValidationResult with issues and proceed flag.
        """
        start = time.time()

        try:
            config = get_proxy_config("flash")
            prompt = self._build_prompt(task)

            payload = {
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "model": "flash",
            }

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{config.base_url}/v1/chat/completions",
                    json=payload,
                )
                latency_ms = int((time.time() - start) * 1000)

                if response.status_code != 200:
                    return TicketValidationResult(
                        ticket_id=task.id,
                        error=f"HTTP {response.status_code}: {response.text}",
                        latency_ms=latency_ms,
                        proceed=False,
                    )

                data = response.json()
                content = data["choices"][0]["message"]["content"]

                # Parse the YAML response
                parsed = _parse_yaml_response(content)

                issues = [
                    ValidationIssue(
                        dimension=i["dimension"],
                        issue=i["issue"],
                        severity=i["severity"],
                    )
                    for i in parsed.get("issues", [])
                ]

                high_count = parsed.get("high_count", sum(1 for i in issues if i.severity == "HIGH"))
                med_count = parsed.get("med_count", sum(1 for i in issues if i.severity == "MED"))
                low_count = parsed.get("low_count", sum(1 for i in issues if i.severity == "LOW"))

                return TicketValidationResult(
                    ticket_id=task.id,
                    issues=issues,
                    high_count=high_count,
                    med_count=med_count,
                    low_count=low_count,
                    proceed=high_count == 0,
                    latency_ms=latency_ms,
                )

        except httpx.TimeoutException:
            latency_ms = int((time.time() - start) * 1000)
            return TicketValidationResult(
                ticket_id=task.id,
                error="Request timeout to flash proxy",
                latency_ms=latency_ms,
                proceed=False,
            )
        except httpx.ConnectError as e:
            latency_ms = int((time.time() - start) * 1000)
            return TicketValidationResult(
                ticket_id=task.id,
                error=f"Connection failed to flash proxy: {e}",
                latency_ms=latency_ms,
                proceed=False,
            )
        except TicketValidationError as e:
            latency_ms = int((time.time() - start) * 1000)
            return TicketValidationResult(
                ticket_id=task.id,
                error=str(e),
                latency_ms=latency_ms,
                proceed=False,
            )
        except Exception as e:
            latency_ms = int((time.time() - start) * 1000)
            return TicketValidationResult(
                ticket_id=task.id,
                error=f"Validation error: {e}",
                latency_ms=latency_ms,
                proceed=False,
            )

    def validate_queue(self, queue: QueueModel) -> BatchValidationResult:
        """Validate all tasks in a queue.

        Args:
            queue: QueueModel containing tasks to validate.

        Returns:
            BatchValidationResult with all individual results and summary.
        """
        results = []
        proceed_count = 0
        blocked_count = 0
        error_count = 0

        for task in queue.tasks:
            result = self.validate_ticket(task)
            results.append(result)

            if result.error:
                error_count += 1
            elif result.proceed:
                proceed_count += 1
            else:
                blocked_count += 1

        return BatchValidationResult(
            results=results,
            total_count=len(queue.tasks),
            proceed_count=proceed_count,
            blocked_count=blocked_count,
            error_count=error_count,
        )
