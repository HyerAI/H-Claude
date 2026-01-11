"""Queue manager for H-Conductor execution loop.

This module provides the QueueManager class that handles loading,
saving, and updating the queue.json file with atomic writes.
"""

import fcntl
import json
from pathlib import Path
from typing import Optional

from orchestrator.models import QueueModel, TaskStatus


class QueueManager:
    """Manages queue.json file operations.

    Provides atomic read/write operations with file locking
    to prevent corruption from concurrent access.

    Example:
        manager = QueueManager("/path/to/queue.json")
        queue = manager.load()
        manager.update_task_status("task_001", TaskStatus.IN_PROGRESS)
    """

    def __init__(self, queue_path: str) -> None:
        """Initialize QueueManager.

        Args:
            queue_path: Path to queue.json file.
        """
        self.queue_path = Path(queue_path)

    def load(self) -> QueueModel:
        """Load queue from disk.

        Returns:
            QueueModel parsed from queue.json.

        Raises:
            FileNotFoundError: If queue.json doesn't exist.
            ValueError: If queue.json is invalid.
        """
        if not self.queue_path.exists():
            raise FileNotFoundError(f"Queue file not found: {self.queue_path}")

        with open(self.queue_path, "r") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return QueueModel(**data)

    def save(self, queue: QueueModel) -> None:
        """Save queue to disk atomically.

        Uses temp file + rename for atomic writes (POSIX-safe).
        Lock is held until atomic rename completes.

        Args:
            queue: QueueModel to save.
        """
        # Serialize to JSON
        data = queue.model_dump(mode="json")

        # Write to temp file first
        temp_path = self.queue_path.with_suffix(".tmp")

        with open(temp_path, "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(data, f, indent=2)
                f.flush()
                # Atomic rename inside lock context
                temp_path.replace(self.queue_path)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def update_task_status(self, task_id: str, status: TaskStatus) -> None:
        """Update a task's status in the queue file.

        Performs atomic read-modify-write operation with lock held throughout.

        Args:
            task_id: ID of the task to update.
            status: New status value.

        Raises:
            KeyError: If task_id is not found in queue.
        """
        if not self.queue_path.exists():
            raise FileNotFoundError(f"Queue file not found: {self.queue_path}")

        # Single atomic read-modify-write with lock held throughout
        with open(self.queue_path, "r+") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                # Read
                data = json.load(f)

                # Find and update task
                task_found = False
                for task_data in data["tasks"]:
                    if task_data["id"] == task_id:
                        task_data["status"] = status.value
                        task_found = True
                        break

                if not task_found:
                    raise KeyError(f"Task not found: {task_id}")

                # Write atomically via temp file + rename (while holding lock)
                temp_path = self.queue_path.with_suffix(".tmp")
                with open(temp_path, "w") as tmp_f:
                    json.dump(data, tmp_f, indent=2)

                # Atomic rename while still holding lock on original file
                temp_path.replace(self.queue_path)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
