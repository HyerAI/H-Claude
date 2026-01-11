"""Content normalization and hash comparison utilities.

This module provides functions for normalizing file content and computing
content-based hashes for change detection.
"""

import hashlib
import re
from pathlib import Path


def normalize_for_hash(content: str) -> str:
    """Normalize content for consistent hashing.

    Applies the following normalizations:
    - Normalize line endings (CRLF and CR to LF)
    - Reduce multiple blank lines (3+) to single blank line
    - Strip leading/trailing whitespace

    Args:
        content: Raw content string to normalize.

    Returns:
        Normalized content string.
    """
    # Normalize line endings: CRLF -> LF, CR -> LF
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")

    # Reduce 3+ consecutive newlines to 2 (single blank line)
    # Pattern matches 4+ newlines (3+ blank lines) and replaces with 2
    normalized = re.sub(r"\n{4,}", "\n\n", normalized)

    # Strip leading/trailing whitespace
    normalized = normalized.strip()

    return normalized


def compute_hash(file_path: str) -> str:
    """Compute SHA256 hash of normalized file content.

    Args:
        file_path: Path to the file to hash.

    Returns:
        SHA256 hex digest of normalized content.

    Raises:
        FileNotFoundError: If file does not exist.
    """
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")
    normalized = normalize_for_hash(content)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def check_hash_changed(file_path: str, stored_hash: str) -> bool:
    """Check if file content hash differs from stored hash.

    Args:
        file_path: Path to the file to check.
        stored_hash: Previously computed hash to compare against.

    Returns:
        True if current hash differs from stored hash, False if same.

    Raises:
        FileNotFoundError: If file does not exist.
    """
    current_hash = compute_hash(file_path)
    return current_hash != stored_hash
