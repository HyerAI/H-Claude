"""Model dispatcher for H-Conductor orchestration.

Routes tasks to appropriate model proxies based on task type:
- tdd_worker -> Flash (fast execution)
- qa_review -> Pro (quality review)
- strategic_filter -> Opus (strategic decisions)
- memory_update -> Opus (context management)
- ticket_validation -> Flash (pre-execution validation)

Provides health checking and batch status for all proxies.
"""

import time
from dataclasses import dataclass
from typing import Optional

import httpx

from orchestrator.config import get_proxy_config, ConfigError
from orchestrator.prompts import get_prompt, TemplateNotFoundError


class UnknownTaskTypeError(Exception):
    """Raised when a task type is not recognized."""

    pass


class ParseError(Exception):
    """Raised when response parsing fails completely."""

    pass


@dataclass
class HealthCheckResult:
    """Result of a proxy health check.

    Attributes:
        healthy: Whether the proxy is responding.
        latency_ms: Response time in milliseconds (0 if unhealthy).
        error: Error message if unhealthy, None otherwise.
    """

    healthy: bool
    latency_ms: int
    error: Optional[str]


@dataclass
class AllProxiesHealthResult:
    """Health status of all three model proxies.

    Attributes:
        flash: Health check result for flash proxy.
        pro: Health check result for pro proxy.
        opus: Health check result for opus proxy.
    """

    flash: HealthCheckResult
    pro: HealthCheckResult
    opus: HealthCheckResult

    @property
    def overall_status(self) -> str:
        """Get overall status: all_healthy, degraded, or offline."""
        healthy_count = sum(
            1 for r in [self.flash, self.pro, self.opus] if r.healthy
        )
        if healthy_count == 3:
            return "all_healthy"
        elif healthy_count > 0:
            return "degraded"
        else:
            return "offline"

    @property
    def summary(self) -> str:
        """Human-readable summary of proxy status."""
        lines = []
        for name, result in [
            ("Flash", self.flash),
            ("Pro", self.pro),
            ("Opus", self.opus),
        ]:
            if result.healthy:
                lines.append(f"{name}: OK ({result.latency_ms}ms)")
            else:
                lines.append(f"{name}: FAIL ({result.error})")
        return " | ".join(lines)


@dataclass
class DispatchResult:
    """Result of dispatching a request to a model proxy.

    Attributes:
        success: Whether the request succeeded.
        response: Model response text if successful.
        latency_ms: Request time in milliseconds.
        error: Error message if failed, None otherwise.
    """

    success: bool
    response: str
    latency_ms: int
    error: Optional[str]


@dataclass
class ParsedResponse:
    """Parsed response from a model.

    Attributes:
        content: Extracted content (code, JSON, text, or decision).
        format: The format that was parsed.
        warnings: Any warnings during parsing.
    """

    content: str
    format: str
    warnings: list[str]


# Task type to model mapping
TASK_TYPE_ROUTING: dict[str, str] = {
    "tdd_worker": "flash",
    "qa_review": "pro",
    "strategic_filter": "opus",
    "memory_update": "opus",
    "ticket_validation": "flash",
}


def check_proxy_health(
    model_name: str, timeout: float = 5.0
) -> HealthCheckResult:
    """Check if a model proxy is healthy.

    Attempts to connect to the proxy's base URL.

    Args:
        model_name: One of 'flash', 'pro', or 'opus'.
        timeout: Connection timeout in seconds (default 5.0).

    Returns:
        HealthCheckResult with health status and latency.
    """
    config = get_proxy_config(model_name)

    start = time.time()
    try:
        with httpx.Client(timeout=timeout) as client:
            # Try to connect to the proxy base URL
            response = client.get(config.base_url)
            latency_ms = int((time.time() - start) * 1000)
            return HealthCheckResult(healthy=True, latency_ms=latency_ms, error=None)
    except httpx.TimeoutException:
        latency_ms = int((time.time() - start) * 1000)
        return HealthCheckResult(
            healthy=False,
            latency_ms=latency_ms,
            error=f"Timeout connecting to {model_name} proxy at {config.base_url}",
        )
    except httpx.ConnectError as e:
        latency_ms = int((time.time() - start) * 1000)
        return HealthCheckResult(
            healthy=False,
            latency_ms=latency_ms,
            error=f"Connection failed to {model_name} proxy: {str(e)}",
        )
    except Exception as e:
        latency_ms = int((time.time() - start) * 1000)
        return HealthCheckResult(
            healthy=False,
            latency_ms=latency_ms,
            error=f"Error checking {model_name} proxy: {str(e)}",
        )


def check_all_proxies(timeout: float = 5.0) -> AllProxiesHealthResult:
    """Check health of all three model proxies.

    Args:
        timeout: Connection timeout for each check.

    Returns:
        AllProxiesHealthResult with status of each proxy.
    """
    flash = check_proxy_health("flash", timeout=timeout)
    pro = check_proxy_health("pro", timeout=timeout)
    opus = check_proxy_health("opus", timeout=timeout)
    return AllProxiesHealthResult(flash=flash, pro=pro, opus=opus)


class ModelDispatcher:
    """Routes tasks to appropriate model proxies.

    Provides:
    - Task type -> model routing
    - Request dispatch with retry logic
    - Response parsing

    Example:
        dispatcher = ModelDispatcher()
        result = dispatcher.send_request("tdd_worker", {"task_description": "..."})
    """

    def __init__(self, check_health: bool = True, timeout: float = 30.0):
        """Initialize the dispatcher.

        Args:
            check_health: If True, verify proxy health on init.
            timeout: Default timeout for requests.
        """
        self.timeout = timeout
        self._health_status: Optional[AllProxiesHealthResult] = None

        if check_health:
            self._health_status = check_all_proxies()

    def route_to_model(self, task_type: str) -> str:
        """Determine which model should handle a task type.

        Args:
            task_type: One of 'tdd_worker', 'qa_review', 'strategic_filter', 'memory_update'.

        Returns:
            Model name: 'flash', 'pro', or 'opus'.

        Raises:
            UnknownTaskTypeError: If task_type is not recognized.
        """
        if task_type not in TASK_TYPE_ROUTING:
            raise UnknownTaskTypeError(
                f"Unknown task type: '{task_type}'. "
                f"Valid types: {', '.join(TASK_TYPE_ROUTING.keys())}"
            )
        return TASK_TYPE_ROUTING[task_type]

    def send_request(
        self,
        task_type: str,
        prompt_vars: dict[str, str],
        max_retries: int = 2,
    ) -> DispatchResult:
        """Send a request to the appropriate model proxy.

        Args:
            task_type: The type of task (determines model and prompt).
            prompt_vars: Variables to format the prompt template.
            max_retries: Maximum retries on transient failures.

        Returns:
            DispatchResult with success status, response, and timing.
        """
        # Get model and prompt
        model_name = self.route_to_model(task_type)
        config = get_proxy_config(model_name)
        template = get_prompt(task_type)

        # Format the prompt
        try:
            user_prompt = template.user_prompt_template.format(**prompt_vars)
        except KeyError as e:
            return DispatchResult(
                success=False,
                response="",
                latency_ms=0,
                error=f"Missing prompt variable: {e}",
            )

        # Build request payload (OpenAI-compatible format)
        payload = {
            "messages": [
                {"role": "system", "content": template.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "model": model_name,
        }

        # Send with retries
        last_error = None
        for attempt in range(max_retries + 1):
            start = time.time()
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(
                        f"{config.base_url}/v1/chat/completions",
                        json=payload,
                    )
                    latency_ms = int((time.time() - start) * 1000)

                    if response.status_code == 200:
                        data = response.json()
                        content = data["choices"][0]["message"]["content"]
                        return DispatchResult(
                            success=True,
                            response=content,
                            latency_ms=latency_ms,
                            error=None,
                        )
                    else:
                        last_error = f"HTTP {response.status_code}: {response.text}"

            except httpx.TimeoutException:
                last_error = f"Request timeout to {model_name} proxy"
            except httpx.ConnectError as e:
                last_error = f"Connection failed to {model_name} proxy: {e}"
            except Exception as e:
                last_error = f"Request error: {e}"

            # Exponential backoff before retry
            if attempt < max_retries:
                time.sleep(0.5 * (2 ** attempt))

        latency_ms = int((time.time() - start) * 1000)
        return DispatchResult(
            success=False,
            response="",
            latency_ms=latency_ms,
            error=last_error,
        )

    def parse_response(
        self, raw_response: str, expected_format: str
    ) -> ParsedResponse:
        """Parse a model response into structured content.

        Args:
            raw_response: Raw text from model.
            expected_format: One of 'code', 'json', 'text', 'decision'.

        Returns:
            ParsedResponse with extracted content.

        Raises:
            ParseError: If response cannot be parsed at all.
        """
        import json
        import re

        warnings: list[str] = []

        if expected_format == "text":
            return ParsedResponse(content=raw_response, format="text", warnings=[])

        elif expected_format == "code":
            # Extract code from markdown code blocks
            code_pattern = r"```(?:\w+)?\n(.*?)```"
            matches = re.findall(code_pattern, raw_response, re.DOTALL)
            if matches:
                content = "\n\n".join(matches)
                return ParsedResponse(content=content, format="code", warnings=[])
            else:
                # No code blocks found, return raw (with warning)
                warnings.append("No code blocks found, returning raw response")
                return ParsedResponse(
                    content=raw_response, format="code", warnings=warnings
                )

        elif expected_format == "json":
            # Try to parse JSON from response
            try:
                # Try direct parse
                parsed = json.loads(raw_response)
                return ParsedResponse(
                    content=json.dumps(parsed), format="json", warnings=[]
                )
            except json.JSONDecodeError:
                # Try to extract JSON from markdown
                json_pattern = r"```json\n(.*?)```"
                matches = re.findall(json_pattern, raw_response, re.DOTALL)
                if matches:
                    try:
                        parsed = json.loads(matches[0])
                        return ParsedResponse(
                            content=json.dumps(parsed), format="json", warnings=[]
                        )
                    except json.JSONDecodeError:
                        pass
                raise ParseError(f"Could not parse JSON from response: {raw_response[:100]}...")

        elif expected_format == "decision":
            # Extract APPROVED or REJECTED
            upper = raw_response.upper()
            if "APPROVED" in upper:
                return ParsedResponse(content="APPROVED", format="decision", warnings=[])
            elif "REJECTED" in upper:
                return ParsedResponse(content="REJECTED", format="decision", warnings=[])
            elif "NEEDS_REFINEMENT" in upper:
                return ParsedResponse(
                    content="NEEDS_REFINEMENT", format="decision", warnings=[]
                )
            else:
                raise ParseError(
                    f"Could not extract decision (APPROVED/REJECTED) from: {raw_response[:100]}..."
                )

        else:
            raise ParseError(f"Unknown format: {expected_format}")
