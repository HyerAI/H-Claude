"""DNA Drift Check module for H-Conductor.

This module implements the DNA traceability system that ensures every task
traces back to a NorthStar goal. It prevents "orphan features" - code that
doesn't connect to any strategic objective.

DNA Traceability: Goal 4 - "Every ticket must trace back to NorthStar; reject orphan features"
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from orchestrator.models import TaskModel, QueueModel


class NorthStarError(Exception):
    """Raised when NorthStar parsing fails."""

    pass


class TaskNotFoundError(Exception):
    """Raised when a task ID is not found in the queue."""

    pass


@dataclass
class LineageResult:
    """Result of a lineage check for a single task.

    Attributes:
        valid: Whether the task traces to a NorthStar goal.
        matched_goal: The goal ID that was matched (e.g., "goal_4"), or None if no match.
        message: Descriptive message about the lineage result.
    """

    valid: bool
    matched_goal: Optional[str]
    message: str


@dataclass
class DNAValidationResult:
    """Result of validating all tasks in a queue for DNA traceability.

    Attributes:
        valid: True if all tasks trace to NorthStar goals.
        orphan_tasks: List of task IDs that don't trace to any goal.
        valid_tasks: List of task IDs that have valid lineage.
    """

    valid: bool
    orphan_tasks: list[str]
    valid_tasks: list[str]


@dataclass
class MergeGateResult:
    """Result of pre-merge DNA gate check.

    Attributes:
        approved: Whether the merge is approved.
        reason: Explanation of the decision.
    """

    approved: bool
    reason: str


def parse_northstar(path: str) -> dict[str, str]:
    """Parse NORTHSTAR.md and extract goals.

    Args:
        path: Path to the NORTHSTAR.md file.

    Returns:
        Dictionary mapping goal IDs (e.g., "goal_1") to goal descriptions.

    Raises:
        NorthStarError: If the file is not found or cannot be parsed.
    """
    filepath = Path(path)
    if not filepath.exists():
        raise NorthStarError(f"NorthStar file not found: {path}")

    content = filepath.read_text()

    goals: dict[str, str] = {}

    # Look for goals section
    goals_section_match = re.search(
        r"##\s*Goals\s*\n(.*?)(?:\n##|\Z)", content, re.DOTALL | re.IGNORECASE
    )

    if not goals_section_match:
        return goals

    goals_text = goals_section_match.group(1)

    # Match numbered goals: "N. **Title** - Description" or "N. **Title**"
    goal_pattern = re.compile(
        r"(\d+)\.\s*\*\*([^*]+)\*\*(?:\s*[-\u2013\u2014]\s*(.+?))?(?=\n\d+\.|\n##|\Z)",
        re.DOTALL,
    )

    for match in goal_pattern.finditer(goals_text):
        goal_num = match.group(1)
        goal_title = match.group(2).strip()
        goal_desc = match.group(3).strip() if match.group(3) else ""

        goal_id = f"goal_{goal_num}"
        full_description = f"{goal_title} - {goal_desc}" if goal_desc else goal_title
        goals[goal_id] = full_description

    return goals


def normalize_goal(goal_text: str) -> str:
    """Normalize a goal string for comparison.

    Converts various goal formats to a normalized form for matching:
    - "Goal 4: DNA Drift Check" -> "goal_4"
    - "DNA Drift Check" -> "dna_drift_check"

    Args:
        goal_text: The goal text to normalize.

    Returns:
        Normalized goal key for matching.
    """
    text = goal_text.strip().lower()

    # Check for "Goal N:" format
    goal_num_match = re.match(r"goal\s+(\d+)\s*[:\-]?\s*(.*)", text, re.IGNORECASE)
    if goal_num_match:
        return f"goal_{goal_num_match.group(1)}"

    # Otherwise, normalize description to snake_case
    # Remove special characters except alphanumeric and spaces
    cleaned = re.sub(r"[^\w\s]", "", text)
    # Replace spaces with underscores
    normalized = re.sub(r"\s+", "_", cleaned.strip())

    return normalized


def check_lineage(task: TaskModel, northstar_goals: dict[str, str]) -> LineageResult:
    """Check if a task traces to a NorthStar goal.

    Args:
        task: The task to check.
        northstar_goals: Dictionary of NorthStar goals from parse_northstar().

    Returns:
        LineageResult indicating whether the task has valid lineage.
    """
    task_goal_normalized = normalize_goal(task.northstar_goal)

    # Try exact match on goal ID (e.g., "goal_4")
    if task_goal_normalized in northstar_goals:
        return LineageResult(
            valid=True,
            matched_goal=task_goal_normalized,
            message=f"Task '{task.id}' traces to {task_goal_normalized}: {northstar_goals[task_goal_normalized]}",
        )

    # Try partial match on goal descriptions
    task_goal_lower = task.northstar_goal.lower()
    for goal_id, goal_desc in northstar_goals.items():
        goal_desc_lower = goal_desc.lower()
        # Check if task goal contains key terms from NorthStar goal
        # or if NorthStar goal contains the task goal description
        task_keywords = set(
            re.sub(r"[^\w\s]", "", task_goal_lower).split()
        ) - {"goal", "the", "a", "an", "and", "or", "to", "in", "for"}
        goal_keywords = set(
            re.sub(r"[^\w\s]", "", goal_desc_lower).split()
        ) - {"goal", "the", "a", "an", "and", "or", "to", "in", "for"}

        # Require at least 2 matching keywords or significant overlap
        matching = task_keywords & goal_keywords
        # Guard: Check task_keywords is non-empty before division to avoid ZeroDivisionError
        has_significant_overlap = (
            len(task_keywords) > 0 and len(matching) / len(task_keywords) >= 0.5
        )
        if len(matching) >= 2 or has_significant_overlap:
            return LineageResult(
                valid=True,
                matched_goal=goal_id,
                message=f"Task '{task.id}' traces to {goal_id} (partial match): {goal_desc}",
            )

    return LineageResult(
        valid=False,
        matched_goal=None,
        message=f"Task '{task.id}' has no matching goal in NorthStar. "
        f"northstar_goal='{task.northstar_goal}' does not trace to any defined goal.",
    )


def validate_queue_dna(queue_path: str, northstar_path: str) -> DNAValidationResult:
    """Validate all tasks in a queue for DNA traceability.

    Args:
        queue_path: Path to queue.json file.
        northstar_path: Path to NORTHSTAR.md file.

    Returns:
        DNAValidationResult with lists of valid and orphan tasks.

    Raises:
        NorthStarError: If NorthStar file cannot be parsed.
        ValueError: If queue file is invalid.
    """
    # Parse NorthStar goals
    goals = parse_northstar(northstar_path)

    # Load queue
    queue_file = Path(queue_path)
    if not queue_file.exists():
        raise ValueError(f"Queue file not found: {queue_path}")

    queue_data = json.loads(queue_file.read_text())
    queue = QueueModel(**queue_data)

    valid_tasks: list[str] = []
    orphan_tasks: list[str] = []

    for task in queue.tasks:
        result = check_lineage(task, goals)
        if result.valid:
            valid_tasks.append(task.id)
        else:
            orphan_tasks.append(task.id)

    return DNAValidationResult(
        valid=len(orphan_tasks) == 0,
        orphan_tasks=orphan_tasks,
        valid_tasks=valid_tasks,
    )


def check_task_before_merge(
    task_id: str, queue_path: str, northstar_path: str
) -> MergeGateResult:
    """Check if a specific task can be merged (DNA gate).

    Args:
        task_id: The task ID to check.
        queue_path: Path to queue.json file.
        northstar_path: Path to NORTHSTAR.md file.

    Returns:
        MergeGateResult indicating approval status.

    Raises:
        TaskNotFoundError: If task_id is not in the queue.
        NorthStarError: If NorthStar file cannot be parsed.
    """
    # Parse NorthStar goals
    goals = parse_northstar(northstar_path)

    # Load queue and find task
    queue_file = Path(queue_path)
    if not queue_file.exists():
        raise ValueError(f"Queue file not found: {queue_path}")

    queue_data = json.loads(queue_file.read_text())
    queue = QueueModel(**queue_data)

    task = None
    for t in queue.tasks:
        if t.id == task_id:
            task = t
            break

    if task is None:
        raise TaskNotFoundError(f"Task '{task_id}' not found in queue")

    # Check lineage
    lineage = check_lineage(task, goals)

    if lineage.valid:
        return MergeGateResult(
            approved=True,
            reason=f"Merge approved: {lineage.message}",
        )
    else:
        return MergeGateResult(
            approved=False,
            reason=f"DNA drift detected - orphan task: {lineage.message}",
        )


def main() -> int:
    """CLI entry point for DNA validation.

    Returns:
        Exit code: 0 if all tasks valid, 1 if orphans found.
    """
    parser = argparse.ArgumentParser(
        description="Validate queue tasks against NorthStar goals (DNA drift check)"
    )
    parser.add_argument(
        "--queue",
        required=True,
        help="Path to queue.json file",
    )
    parser.add_argument(
        "--northstar",
        required=True,
        help="Path to NORTHSTAR.md file",
    )

    args = parser.parse_args()

    try:
        result = validate_queue_dna(args.queue, args.northstar)

        print("=" * 60)
        print("DNA DRIFT CHECK REPORT")
        print("=" * 60)
        print(f"Queue: {args.queue}")
        print(f"NorthStar: {args.northstar}")
        print("-" * 60)
        print(f"Valid tasks: {len(result.valid_tasks)}")
        print(f"Orphan tasks: {len(result.orphan_tasks)}")
        print("-" * 60)

        if result.valid:
            print("STATUS: PASS - All tasks trace to NorthStar goals")
            return 0
        else:
            print("STATUS: FAIL - Orphan tasks detected!")
            print("\nOrphan tasks (no NorthStar lineage):")
            for task_id in result.orphan_tasks:
                print(f"  - {task_id}")
            return 1

    except NorthStarError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
