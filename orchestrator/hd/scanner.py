"""NORTHSTAR link scanner with orphan pruning.

This module scans NORTHSTAR.md for checkbox items with links to ADRs/,
UserStories/, or Specs/ directories, and provides orphan task detection.
"""

import re
from pathlib import Path
from typing import Set


# Pattern for markdown checkbox items with links
# Matches: - [ ] text -> [Name](path.md) or - [x] text -> [Name](path.md)
CHECKBOX_LINK_PATTERN = re.compile(
    r"^[\s-]*\[([xX ])\].*?\[([^\]]+)\]\(([^)]+)\)",
    re.MULTILINE,
)

# Valid source directories (links to these are tracked)
VALID_SOURCE_DIRS = {"ADRs/", "UserStories/", "Specs/"}

# Ignored directories (links to these are skipped)
IGNORED_DIRS = {"BACKLOG/"}


def scan_northstar(northstar_path: str) -> list[dict]:
    """Scan NORTHSTAR.md for checkbox items with links to SSoT directories.

    Finds all checklist items with links to ADRs/, UserStories/, or Specs/.
    Ignores links to BACKLOG/ directory.

    Args:
        northstar_path: Path to NORTHSTAR.md file.

    Returns:
        List of dicts with keys:
        - name: Link text (e.g., "ADR-001")
        - source_file: Link path (e.g., "ADRs/adr-001.md")
        - checked: True if checkbox is checked [x], False if unchecked [ ]

    Raises:
        FileNotFoundError: If northstar_path doesn't exist.
    """
    path = Path(northstar_path)
    if not path.exists():
        raise FileNotFoundError(f"NORTHSTAR file not found: {northstar_path}")

    content = path.read_text()
    results = []

    for match in CHECKBOX_LINK_PATTERN.finditer(content):
        checkbox_state = match.group(1)
        link_name = match.group(2)
        link_path = match.group(3)

        # Skip if link is to BACKLOG/
        if any(link_path.startswith(ignored) for ignored in IGNORED_DIRS):
            continue

        # Skip if link is not to a valid source directory
        if not any(link_path.startswith(valid) for valid in VALID_SOURCE_DIRS):
            continue

        results.append({
            "name": link_name,
            "source_file": link_path,
            "checked": checkbox_state.lower() == "x",
        })

    return results


def get_active_links(northstar_path: str) -> Set[str]:
    """Get set of source_file paths for unchecked items only.

    Args:
        northstar_path: Path to NORTHSTAR.md file.

    Returns:
        Set of source_file paths for unchecked (active) items.

    Raises:
        FileNotFoundError: If northstar_path doesn't exist.
    """
    items = scan_northstar(northstar_path)
    return {item["source_file"] for item in items if not item["checked"]}


def get_all_links(northstar_path: str) -> Set[str]:
    """Get set of all source_file paths (both checked and unchecked).

    Args:
        northstar_path: Path to NORTHSTAR.md file.

    Returns:
        Set of all source_file paths found in NORTHSTAR.

    Raises:
        FileNotFoundError: If northstar_path doesn't exist.
    """
    items = scan_northstar(northstar_path)
    return {item["source_file"] for item in items}


def prune_orphans(queue_tasks: list, northstar_path: str) -> list[dict]:
    """Find tasks that should be cancelled due to orphaned source files.

    A task is an orphan if:
    1. It has no source_file field
    2. Its source_file is in NORTHSTAR but checked (inactive/done)
    3. It depends on an orphan task (cascade)

    Tasks whose source_file is NOT in NORTHSTAR are NOT considered orphans
    (they may be valid implementation sub-tasks).

    Args:
        queue_tasks: List of task dicts with keys 'id', 'source_file', 'dependencies'.
        northstar_path: Path to NORTHSTAR.md file.

    Returns:
        List of dicts with keys:
        - task_id: ID of task to cancel
        - reason: Explanation for cancellation

    Note: Caller is responsible for updating task status based on returned orphans.
    """
    if not queue_tasks:
        return []

    active_links = get_active_links(northstar_path)
    all_links = get_all_links(northstar_path)
    orphan_ids: set[str] = set()
    results: list[dict] = []

    # First pass: identify direct orphans
    for task in queue_tasks:
        task_id = task.get("id")
        if not task_id:
            continue  # Skip tasks without id
        source_file = task.get("source_file")

        if source_file is None:
            orphan_ids.add(task_id)
            results.append({
                "task_id": task_id,
                "reason": "No source_file field - cannot trace to NORTHSTAR",
            })
        elif source_file in all_links and source_file not in active_links:
            # Source file is in NORTHSTAR but checked (done/inactive)
            orphan_ids.add(task_id)
            results.append({
                "task_id": task_id,
                "reason": f"Source file '{source_file}' not in active links",
            })
        # Note: if source_file not in all_links, task is NOT an orphan
        # (it may be a valid sub-task not tracked in NORTHSTAR)

    # Second pass: cascade to dependents
    # Build dependency graph (task_id -> list of tasks that depend on it)
    dependents: dict[str, list[str]] = {}
    for task in queue_tasks:
        task_id = task.get("id")
        if not task_id:
            continue  # Skip tasks without id
        for dep in task.get("dependencies", []):
            if dep not in dependents:
                dependents[dep] = []
            dependents[dep].append(task_id)

    # BFS to find all cascading orphans
    queue = list(orphan_ids)
    visited = set(orphan_ids)

    while queue:
        current = queue.pop(0)
        for dependent_id in dependents.get(current, []):
            if dependent_id not in visited:
                visited.add(dependent_id)
                orphan_ids.add(dependent_id)
                queue.append(dependent_id)
                results.append({
                    "task_id": dependent_id,
                    "reason": f"Depends on orphan task '{current}'",
                })

    return results
