"""H-Conductor CLI commands.

Provides unified CLI interface for H-Conductor operations:
- hc status: Show queue status summary
- hc queue: Manage task queue
- hc run: Execute orchestration loop
- hc scan: Scan NORTHSTAR for activated items (HD Interface)
- hc validate: Validate file against Definition of Ready (HD Interface)
- hc inbox: Display INBOX.md contents (HD Interface)

Usage:
    python -m orchestrator.cli status --queue queue.json
    python -m orchestrator.cli queue list --queue queue.json
    python -m orchestrator.cli run --queue queue.json
    python -m orchestrator.cli scan --northstar .claude/PM/SSoT/NORTHSTAR.md
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional


def status_command(queue_path: str) -> dict[str, Any]:
    """Show queue status summary.

    Args:
        queue_path: Path to queue.json file.

    Returns:
        Dictionary with:
        - summary: counts by status (open, in_progress, complete, blocked, total)
        - current_task: dict with id/description of in_progress task, or None
        - error: error message if failed, or None
    """
    path = Path(queue_path)

    if not path.exists():
        return {"summary": {}, "current_task": None, "error": f"Queue file not found: {queue_path}"}

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {"summary": {}, "current_task": None, "error": f"Invalid JSON: {e}"}

    tasks = data.get("tasks", [])

    # Count by status
    summary = {
        "open": 0,
        "in_progress": 0,
        "complete": 0,
        "blocked": 0,
        "review": 0,
        "total": len(tasks),
    }

    current_task = None

    for task in tasks:
        status = task.get("status", "open")
        if status in summary:
            summary[status] += 1

        if status == "in_progress" and current_task is None:
            current_task = {
                "id": task.get("id"),
                "description": task.get("description"),
            }

    return {"summary": summary, "current_task": current_task, "error": None}


def queue_command(
    action: str,
    queue_path: str,
    task_id: Optional[str] = None,
    description: Optional[str] = None,
    northstar_goal: Optional[str] = None,
    priority: Optional[int] = None,
) -> dict[str, Any]:
    """Manage task queue.

    Args:
        action: One of "list", "show", "add".
        queue_path: Path to queue.json file.
        task_id: Task ID (for show/add).
        description: Task description (for add).
        northstar_goal: NorthStar goal (for add).
        priority: Task priority (for add).

    Returns:
        Dictionary with operation result.
    """
    path = Path(queue_path)

    if action == "list":
        return _queue_list(path)
    elif action == "show":
        return _queue_show(path, task_id)
    elif action == "add":
        return _queue_add(path, task_id, description, northstar_goal, priority)
    else:
        return {"error": f"Unknown action: {action}"}


def _queue_list(path: Path) -> dict[str, Any]:
    """List all tasks in the queue."""
    if not path.exists():
        return {"tasks": [], "error": f"Queue file not found: {path}"}

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {"tasks": [], "error": f"Invalid JSON: {e}"}

    return {"tasks": data.get("tasks", []), "error": None}


def _queue_show(path: Path, task_id: Optional[str]) -> dict[str, Any]:
    """Show details of a specific task."""
    if not path.exists():
        return {"task": None, "error": f"Queue file not found: {path}"}

    if not task_id:
        return {"task": None, "error": "Task ID required"}

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {"task": None, "error": f"Invalid JSON: {e}"}

    for task in data.get("tasks", []):
        if task.get("id") == task_id:
            return {"task": task, "error": None}

    return {"task": None, "error": f"Task not found: {task_id}"}


def _queue_add(
    path: Path,
    task_id: Optional[str],
    description: Optional[str],
    northstar_goal: Optional[str],
    priority: Optional[int],
) -> dict[str, Any]:
    """Add a new task to the queue."""
    if not path.exists():
        return {"success": False, "error": f"Queue file not found: {path}"}

    if not task_id:
        return {"success": False, "error": "Task ID required"}
    if not description:
        return {"success": False, "error": "Description required"}
    if not northstar_goal:
        return {"success": False, "error": "NorthStar goal required"}

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Invalid JSON: {e}"}

    # Check for duplicate ID
    for task in data.get("tasks", []):
        if task.get("id") == task_id:
            return {"success": False, "error": f"Task already exists: {task_id}"}

    # Create new task
    new_task = {
        "id": task_id,
        "status": "open",
        "priority": priority or 10,
        "description": description,
        "northstar_goal": northstar_goal,
        "dependencies": [],
        "files": [],
    }

    data.setdefault("tasks", []).append(new_task)

    # Atomic write: write to temp file first, then os.replace (atomic on POSIX)
    dir_path = path.parent
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=dir_path,
            suffix=".tmp",
            delete=False,
        ) as tmp_file:
            json.dump(data, tmp_file, indent=2)
            tmp_path = tmp_file.name
        os.replace(tmp_path, path)
    except Exception as e:
        # Clean up temp file if it exists
        if "tmp_path" in locals() and Path(tmp_path).exists():
            Path(tmp_path).unlink()
        return {"success": False, "error": f"Failed to write queue file: {e}"}

    return {"success": True, "task_id": task_id, "error": None}


def _print_status(result: dict[str, Any]) -> None:
    """Pretty-print status result to stdout."""
    if result.get("error"):
        print(f"Error: {result['error']}")
        return

    summary = result["summary"]
    print("Queue Status")
    print("=" * 40)
    print(f"  Open:        {summary.get('open', 0)}")
    print(f"  In Progress: {summary.get('in_progress', 0)}")
    print(f"  Review:      {summary.get('review', 0)}")
    print(f"  Complete:    {summary.get('complete', 0)}")
    print(f"  Blocked:     {summary.get('blocked', 0)}")
    print(f"  Total:       {summary.get('total', 0)}")

    if result.get("current_task"):
        task = result["current_task"]
        print()
        print("Current Task:")
        print(f"  ID:   {task['id']}")
        print(f"  Desc: {task['description']}")


def _print_queue_list(result: dict[str, Any]) -> None:
    """Pretty-print queue list to stdout."""
    if result.get("error"):
        print(f"Error: {result['error']}")
        return

    tasks = result.get("tasks", [])
    if not tasks:
        print("No tasks in queue.")
        return

    print("Task Queue")
    print("=" * 60)
    print(f"{'ID':<15} {'Status':<12} {'Priority':<8} Description")
    print("-" * 60)

    for task in tasks:
        task_id = task.get("id", "")[:14]
        status = task.get("status", "")[:11]
        priority = task.get("priority", 0)
        desc = task.get("description", "")[:30]
        print(f"{task_id:<15} {status:<12} {priority:<8} {desc}")


def _print_queue_show(result: dict[str, Any]) -> None:
    """Pretty-print task details to stdout."""
    if result.get("error"):
        print(f"Error: {result['error']}")
        return

    task = result.get("task")
    if not task:
        print("Task not found.")
        return

    print("Task Details")
    print("=" * 40)
    print(f"  ID:          {task.get('id')}")
    print(f"  Status:      {task.get('status')}")
    print(f"  Priority:    {task.get('priority')}")
    print(f"  Description: {task.get('description')}")
    print(f"  NorthStar:   {task.get('northstar_goal')}")

    deps = task.get("dependencies", [])
    if deps:
        print(f"  Dependencies: {', '.join(deps)}")

    files = task.get("files", [])
    if files:
        print(f"  Files:       {', '.join(files)}")


def _validate_queue_command(queue_path: str, output_path: Optional[str] = None) -> int:
    """Batch validate all pending tickets in queue.

    Args:
        queue_path: Path to queue.json file.
        output_path: Optional path for JSON output.

    Returns:
        Exit code: 0 (success), 1 (error).
    """
    from orchestrator.models import QueueModel
    from orchestrator.ticket_validator import TicketValidator

    path = Path(queue_path)
    if not path.exists():
        print(f"Error: Queue file not found: {queue_path}")
        return 1

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}")
        return 1

    # Parse queue
    try:
        queue = QueueModel.from_dict(data)
    except Exception as e:
        print(f"Error: Failed to parse queue: {e}")
        return 1

    # Validate all tickets
    validator = TicketValidator()
    result = validator.validate_queue(queue)

    # Print summary
    print("Ticket Validation Summary")
    print("=" * 50)
    print(result.summary)
    print()

    # Print details
    for r in result.results:
        status = "PROCEED" if r.proceed else "BLOCKED"
        if r.error:
            status = "ERROR"
        print(f"  {r.ticket_id}: {status}")
        if r.issues:
            for issue in r.issues:
                print(f"    [{issue.severity}] {issue.dimension}: {issue.issue}")
        if r.error:
            print(f"    Error: {r.error}")

    # Write JSON output if requested
    if output_path:
        output = {
            "summary": {
                "total_count": result.total_count,
                "proceed_count": result.proceed_count,
                "blocked_count": result.blocked_count,
                "error_count": result.error_count,
            },
            "results": [r.to_dict() for r in result.results],
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        print(f"\nResults written to: {output_path}")

    return 0 if result.blocked_count == 0 and result.error_count == 0 else 1


def cli_main(args: Optional[list[str]] = None) -> int:
    """Unified CLI entry point for H-Conductor.

    Args:
        args: Command line arguments (uses sys.argv if None).

    Returns:
        Exit code: 0 (success), 1 (error).
    """
    parser = argparse.ArgumentParser(
        prog="hc",
        description="H-Conductor: TDD-driven AI orchestration toolkit",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # status command
    status_parser = subparsers.add_parser("status", help="Show queue status summary")
    status_parser.add_argument(
        "--queue", "-q",
        default="queue.json",
        help="Path to queue.json file",
    )

    # queue command
    queue_parser = subparsers.add_parser("queue", help="Manage task queue")
    queue_subparsers = queue_parser.add_subparsers(dest="queue_action", help="Queue actions")

    # queue list
    list_parser = queue_subparsers.add_parser("list", help="List all tasks")
    list_parser.add_argument(
        "--queue", "-q",
        default="queue.json",
        help="Path to queue.json file",
    )

    # queue show
    show_parser = queue_subparsers.add_parser("show", help="Show task details")
    show_parser.add_argument("task_id", help="Task ID to show")
    show_parser.add_argument(
        "--queue", "-q",
        default="queue.json",
        help="Path to queue.json file",
    )

    # queue add
    add_parser = queue_subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("task_id", help="Task ID")
    add_parser.add_argument("--description", "-d", required=True, help="Task description")
    add_parser.add_argument("--goal", "-g", required=True, help="NorthStar goal")
    add_parser.add_argument("--priority", "-p", type=int, default=10, help="Task priority")
    add_parser.add_argument(
        "--queue", "-q",
        default="queue.json",
        help="Path to queue.json file",
    )

    # HD Interface commands (scan, validate, inbox)
    from orchestrator.hd.cli import register_hd_commands
    register_hd_commands(subparsers)

    # run command
    run_parser = subparsers.add_parser("run", help="Execute orchestration loop")
    run_parser.add_argument(
        "--queue", "-q",
        required=True,
        help="Path to queue.json file",
    )
    run_parser.add_argument(
        "--single", "-1",
        action="store_true",
        help="Execute single task and exit",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing",
    )
    run_parser.add_argument(
        "--northstar",
        default=".claude/PM/SSoT/NORTHSTAR.md",
        help="Path to NORTHSTAR.md file",
    )
    run_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    # Ticket validation flags (Phase 15)
    run_parser.add_argument(
        "--strict-tickets",
        action="store_true",
        help="Block execution on HIGH validation issues",
    )
    run_parser.add_argument(
        "--skip-ticket-validation",
        action="store_true",
        help="Skip ticket validation entirely",
    )

    # validate-queue command (batch ticket validation)
    validate_queue_parser = subparsers.add_parser(
        "validate-queue",
        help="Batch validate all pending tickets without execution",
    )
    validate_queue_parser.add_argument(
        "--queue", "-q",
        required=True,
        help="Path to queue.json file",
    )
    validate_queue_parser.add_argument(
        "--output", "-o",
        help="Output file for validation results (JSON)",
    )

    parsed = parser.parse_args(args)

    if parsed.command == "status":
        result = status_command(parsed.queue)
        _print_status(result)
        return 0 if result.get("error") is None else 1

    elif parsed.command == "queue":
        if parsed.queue_action == "list":
            result = queue_command("list", parsed.queue)
            _print_queue_list(result)
            return 0 if result.get("error") is None else 1

        elif parsed.queue_action == "show":
            result = queue_command("show", parsed.queue, task_id=parsed.task_id)
            _print_queue_show(result)
            return 0 if result.get("error") is None else 1

        elif parsed.queue_action == "add":
            result = queue_command(
                "add",
                parsed.queue,
                task_id=parsed.task_id,
                description=parsed.description,
                northstar_goal=parsed.goal,
                priority=parsed.priority,
            )
            if result.get("success"):
                print(f"Task added: {result['task_id']}")
                return 0
            else:
                print(f"Error: {result.get('error')}")
                return 1

        else:
            queue_parser.print_help()
            return 1

    elif parsed.command == "run":
        # Delegate to main.py execution
        from main import main as run_main

        run_args = ["--queue", parsed.queue]
        if parsed.single:
            run_args.append("--single")
        if parsed.dry_run:
            run_args.append("--dry-run")
        if parsed.northstar:
            run_args.extend(["--northstar", parsed.northstar])
        if parsed.verbose:
            run_args.append("--verbose")
        if parsed.strict_tickets:
            run_args.append("--strict-tickets")
        if parsed.skip_ticket_validation:
            run_args.append("--skip-ticket-validation")

        return run_main(run_args)

    elif parsed.command == "validate-queue":
        return _validate_queue_command(parsed.queue, parsed.output)

    else:
        parser.print_help()
        return 1


def main() -> int:
    """Entry point for console_scripts."""
    return cli_main()


if __name__ == "__main__":
    sys.exit(main())
