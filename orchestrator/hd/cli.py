"""CLI commands for HD Interface."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from orchestrator.hd.scanner import scan_northstar, get_active_links, prune_orphans
from orchestrator.hd.definition_of_ready import validate_file
from orchestrator.hd.inbox_writer import InboxWriter


def cmd_scan(args) -> int:
    """Scan NORTHSTAR for activated items and show validation status."""
    northstar_path = args.northstar or ".claude/PM/SSoT/NORTHSTAR.md"

    if not Path(northstar_path).exists():
        print(f"Error: NORTHSTAR not found at {northstar_path}")
        return 1

    items = scan_northstar(northstar_path)

    # Separate activated (unchecked) and completed (checked)
    activated = [i for i in items if not i["checked"]]
    completed = [i for i in items if i["checked"]]

    print(f"\n{'='*60}")
    print(f"NORTHSTAR Scan: {northstar_path}")
    print(f"{'='*60}\n")

    # Show activated items with validation
    print(f"ACTIVATED ({len(activated)} items):")
    print("-" * 40)

    for item in activated:
        if not Path(item["source_file"]).exists():
            status = "INVALID: file not found"
        else:
            result = validate_file(item["source_file"])
            status = "VALID" if result.valid else f"INVALID: missing {', '.join(result.missing)}"
        print(f"  [ ] {item['name']}")
        print(f"      File: {item['source_file']}")
        print(f"      Status: {status}")
        print()

    if not activated:
        print("  (none)")

    # Show completed
    print(f"\nCOMPLETED ({len(completed)} items):")
    print("-" * 40)

    for item in completed:
        print(f"  [x] {item['name']} -> {item['source_file']}")

    if not completed:
        print("  (none)")

    # Check for orphans if queue provided
    if args.queue:
        import json
        try:
            with open(args.queue, encoding='utf-8') as f:
                queue_data = json.load(f)
            orphans = prune_orphans(queue_data.get("tasks", []), northstar_path)

            print(f"\nORPHANED TASKS ({len(orphans)} items):")
            print("-" * 40)

            for orphan in orphans:
                print(f"  {orphan['task_id']}: {orphan['reason']}")

            if not orphans:
                print("  (none)")
        except Exception as e:
            print(f"\nWarning: Could not check queue: {e}")

    print()
    return 0


def cmd_inbox(args) -> int:
    """Display INBOX.md contents."""
    inbox_path = args.path or ".claude/PM/SSoT/INBOX.md"

    # Display contents
    if not Path(inbox_path).exists():
        print(f"INBOX not found at {inbox_path}")
        return 1

    with open(inbox_path, encoding='utf-8') as f:
        content = f.read()

    print(content)
    return 0


def cmd_validate(args) -> int:
    """Validate a file against Definition of Ready."""
    file_path = args.file

    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        return 1

    result = validate_file(file_path)

    print(f"\nValidation: {file_path}")
    print(f"Doc Type: {result.doc_type}")
    print(f"Status: {'PASS' if result.valid else 'FAIL'}")

    if not result.valid:
        print(f"\nMissing sections:")
        for section in result.missing:
            print(f"  - {section}")
        return 1

    print("\nAll required sections present.")
    return 0


def register_hd_commands(subparsers) -> None:
    """Register HD Interface commands on existing argparse subparsers."""

    # hc scan
    scan_parser = subparsers.add_parser("scan", help="Scan NORTHSTAR for activated items")
    scan_parser.add_argument("--northstar", "-n", help="Path to NORTHSTAR.md")
    scan_parser.add_argument("--queue", "-q", help="Path to queue.json for orphan detection")
    scan_parser.set_defaults(func=cmd_scan)

    # hc inbox
    inbox_parser = subparsers.add_parser("inbox", help="Display INBOX.md contents")
    inbox_parser.add_argument("--path", "-p", help="Path to INBOX.md")
    inbox_parser.set_defaults(func=cmd_inbox)

    # hc validate
    validate_parser = subparsers.add_parser("validate", help="Validate file against Definition of Ready")
    validate_parser.add_argument("file", help="File to validate")
    validate_parser.set_defaults(func=cmd_validate)


def main(argv: Optional[List[str]] = None) -> int:
    """Standalone entry point for python -m orchestrator.hd.cli."""
    parser = argparse.ArgumentParser(
        prog="hd",
        description="HD Interface - Product Owner commands"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    register_hd_commands(subparsers)

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
