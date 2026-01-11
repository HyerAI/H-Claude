"""INBOX.md writer utility for HD Interface.

This module provides the InboxWriter class for logging system messages
to INBOX.md, enabling asynchronous communication from H-Conductor to HD.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

# Valid categories for inbox entries
VALID_CATEGORIES = frozenset({
    "REJECTED",
    "CANCELLED",
    "CHANGED",
    "PAUSED",
    "COMPLETE",
    "RETRY",
    "INFO",
    "ERROR",
})


class InboxWriter:
    """Writer for INBOX.md system messages.

    Appends timestamped entries under date sections, creating the file
    and date sections as needed.
    """

    def __init__(self, inbox_path: str) -> None:
        """Initialize the InboxWriter.

        Args:
            inbox_path: Path to the INBOX.md file.
        """
        self.inbox_path = Path(inbox_path)

    def log(
        self,
        category: str,
        message: str,
        action: Optional[str] = None,
    ) -> bool:
        """Append an entry to INBOX.md.

        Args:
            category: Entry category (REJECTED, CANCELLED, CHANGED, PAUSED,
                     COMPLETE, RETRY, INFO, ERROR).
            message: The message content.
            action: Optional action line to include.

        Returns:
            True if entry was written successfully, False otherwise.
        """
        if category not in VALID_CATEGORIES:
            return False

        try:
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M")

            # Build entry
            entry_lines = [
                f"### [{category}] {time_str}",
                message,
            ]
            if action:
                entry_lines.append(f"Action: {action}")
            entry_lines.append("")  # Trailing newline

            entry = "\n".join(entry_lines)

            # Ensure file exists with header
            if not self.inbox_path.exists():
                self._create_file()

            # Read current content
            content = self.inbox_path.read_text()

            # Find or create date section
            date_header = f"## {date_str}"
            if date_header in content:
                # Insert entry after date header
                idx = content.find(date_header)
                end_of_header = content.find("\n", idx) + 1
                new_content = (
                    content[:end_of_header]
                    + "\n"
                    + entry
                    + content[end_of_header:]
                )
            else:
                # Add new date section after the horizontal rule
                hr_marker = "\n---\n"
                if hr_marker in content:
                    idx = content.find(hr_marker) + len(hr_marker)
                    new_content = (
                        content[:idx]
                        + "\n"
                        + date_header
                        + "\n\n"
                        + entry
                        + content[idx:]
                    )
                else:
                    # Append at end if no HR found
                    new_content = content.rstrip() + "\n\n" + date_header + "\n\n" + entry

            self.inbox_path.write_text(new_content)
            return True

        except (OSError, IOError):
            return False

    def _create_file(self) -> None:
        """Create INBOX.md with standard header."""
        header = """# INBOX

System messages from H-Conductor to HD (Product Owner).

---
"""
        self.inbox_path.parent.mkdir(parents=True, exist_ok=True)
        self.inbox_path.write_text(header)
