"""Schema validation for H-Conductor task queue."""

import json
from pathlib import Path
from typing import Union

from .models import QueueModel


def validate_queue(path: Union[str, Path]) -> QueueModel:
    """Load and validate a queue.json file.

    Args:
        path: Path to the queue.json file (str or Path).

    Returns:
        Validated QueueModel instance.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        json.JSONDecodeError: If the file contains malformed JSON.
        pydantic.ValidationError: If the data doesn't match the schema.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Queue file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return QueueModel.model_validate(data)
