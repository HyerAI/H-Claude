"""Atomic NORTHSTAR checkbox updater.

This module provides functions for atomically updating checkboxes in markdown
files, with retry logic for concurrent modification safety.
"""

import os
import re
import tempfile
from pathlib import Path
from typing import Optional, Tuple


def find_checkbox_line(content: str, source_file: str) -> Optional[Tuple[int, str]]:
    """Find line number and content with matching file link and unchecked checkbox.

    Searches for a line containing both an unchecked checkbox (- [ ]) and a
    markdown link to the specified source file.

    Args:
        content: Full file content to search.
        source_file: Filename or path to match in markdown links.

    Returns:
        Tuple of (line_number, line_content) if found, None otherwise.
        Line numbers are 0-indexed.
    """
    lines = content.split("\n")
    # Escape special regex chars in filename but allow partial path matching
    escaped_file = re.escape(source_file)

    for idx, line in enumerate(lines):
        # Must have unchecked checkbox
        if "- [ ]" not in line:
            continue
        # Must have markdown link containing the source file
        # Pattern: [text](path/to/source_file) or [text](source_file)
        link_pattern = rf"\[.*?\]\([^)]*{escaped_file}[^)]*\)"
        if re.search(link_pattern, line):
            return (idx, line)

    return None


def update_checkbox(line: str) -> str:
    """Replace unchecked checkbox with checked in a line.

    Args:
        line: Line containing "- [ ]" to update.

    Returns:
        Line with "- [ ]" replaced by "- [x]".
    """
    return line.replace("- [ ]", "- [x]", 1)


def atomic_checkbox_update(
    northstar_path: str, source_file: str, max_retries: int = 3
) -> bool:
    """Atomically update a checkbox in the NORTHSTAR file.

    Performs an atomic read-check-write operation with mtime verification
    to handle concurrent modifications safely.

    Algorithm:
    1. Read file content and record mtime
    2. Find and update the checkbox line
    3. Write to temp file in same directory
    4. Check if mtime changed (concurrent modification)
    5. If mtime unchanged, atomic rename temp to target
    6. If mtime changed, retry up to max_retries

    Args:
        northstar_path: Path to the NORTHSTAR markdown file.
        source_file: Filename to find in markdown links.
        max_retries: Maximum retry attempts for concurrent modifications.

    Returns:
        True if checkbox was successfully updated, False otherwise.
    """
    path = Path(northstar_path)

    for attempt in range(max_retries):
        # Step 1: Read content and get mtime
        try:
            stat_before = path.stat()
            mtime_before = stat_before.st_mtime
            content = path.read_text(encoding="utf-8")
        except (OSError, IOError):
            return False

        # Step 2: Find the checkbox line
        result = find_checkbox_line(content, source_file)
        if result is None:
            return False

        line_idx, old_line = result
        new_line = update_checkbox(old_line)

        # Build updated content
        lines = content.split("\n")
        lines[line_idx] = new_line
        new_content = "\n".join(lines)

        # Step 3: Write to temp file in same directory (for atomic rename)
        dir_path = path.parent
        try:
            fd, temp_path = tempfile.mkstemp(
                dir=str(dir_path), prefix=".checkbox_", suffix=".tmp"
            )
            try:
                os.write(fd, new_content.encode("utf-8"))
            finally:
                os.close(fd)
        except (OSError, IOError):
            return False

        # Step 4: Check if mtime changed during our operation
        try:
            stat_after = path.stat()
            mtime_after = stat_after.st_mtime
        except (OSError, IOError):
            os.unlink(temp_path)
            return False

        if mtime_before != mtime_after:
            # Concurrent modification detected - clean up and retry
            os.unlink(temp_path)
            continue

        # Step 5: Atomic rename
        try:
            os.replace(temp_path, str(path))
            return True
        except (OSError, IOError):
            # Clean up temp file on failure
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            return False

    # Exhausted retries
    return False
