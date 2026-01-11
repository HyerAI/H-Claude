"""Definition of Ready validator for SSoT documents.

This module validates that documents have all required sections based on their type.
Document types are detected from filename prefixes (US-, ADR-) or default to Spec.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List


# Required sections by document type
REQUIRED_SECTIONS = {
    "UserStory": ["Description", "Acceptance Criteria", "Boundaries"],
    "ADR": ["Context", "Decision", "Consequences"],
    "Spec": ["Overview", "Requirements", "Constraints"],
}


@dataclass
class ValidationResult:
    """Result of document validation.

    Attributes:
        valid: True if all required sections present.
        missing: List of missing section names.
        doc_type: Detected document type.
        file_path: Path to the validated file.
    """

    valid: bool
    missing: List[str]
    doc_type: str
    file_path: str


def detect_doc_type(file_path: str) -> str:
    """Detect document type from filename.

    Args:
        file_path: Path to the document file.

    Returns:
        Document type: "UserStory", "ADR", or "Spec" (default).
    """
    filename = Path(file_path).name

    if filename.startswith("US-"):
        return "UserStory"
    elif filename.startswith("ADR-"):
        return "ADR"
    else:
        return "Spec"


def _remove_code_blocks(content: str) -> str:
    """Remove fenced code blocks from content.

    Args:
        content: Raw markdown content.

    Returns:
        Content with code blocks removed.
    """
    # Remove fenced code blocks (```...```)
    return re.sub(r"```[\s\S]*?```", "", content)


def _find_sections(content: str) -> List[str]:
    """Find all section headings in content.

    Matches ## or ### headings and extracts the section name.
    Section name is the first word(s) before any punctuation.

    Args:
        content: Markdown content without code blocks.

    Returns:
        List of section names found.
    """
    sections = []

    # Match ## or ### at start of line, capture heading text
    pattern = r"^#{2,3}\s+(.+?)(?:\s*[:(\-]|$)"

    for line in content.split("\n"):
        line = line.strip()
        match = re.match(pattern, line)
        if match:
            section_name = match.group(1).strip()
            sections.append(section_name)

    return sections


def validate_file(file_path: str) -> ValidationResult:
    """Validate a document has all required sections.

    Args:
        file_path: Path to the document file.

    Returns:
        ValidationResult with validation status and details.

    Raises:
        FileNotFoundError: If file does not exist.
    """
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")

    doc_type = detect_doc_type(file_path)
    required = REQUIRED_SECTIONS[doc_type]

    # Remove code blocks before searching for sections
    clean_content = _remove_code_blocks(content)
    found_sections = _find_sections(clean_content)

    # Check which required sections are missing
    missing = []
    for section in required:
        # Check if any found section starts with the required section name
        found = any(
            s.startswith(section) or s == section for s in found_sections
        )
        if not found:
            missing.append(section)

    return ValidationResult(
        valid=len(missing) == 0,
        missing=missing,
        doc_type=doc_type,
        file_path=file_path,
    )
