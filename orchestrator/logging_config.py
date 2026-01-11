"""Structured logging configuration for H-Conductor."""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import IO


class JsonFormatter(logging.Formatter):
    """JSON log formatter for production environments."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


class TextFormatter(logging.Formatter):
    """Human-readable log formatter for development."""

    def __init__(self) -> None:
        fmt = "%(asctime)s | %(levelname)-8s | %(module)s | %(message)s"
        super().__init__(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")


def setup_logging(stream: IO[str] | None = None) -> logging.Logger:
    """Configure and return a logger with structured output.

    Args:
        stream: Output stream for logs. Defaults to sys.stderr.

    Returns:
        Configured logger instance.

    Environment variables:
        LOG_FORMAT: 'json' for JSON output, 'text' for human-readable (default: text)
        LOG_LEVEL: Logging level (default: INFO)
    """
    log_format = os.environ.get("LOG_FORMAT", "text").lower()
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()

    logger = logging.getLogger("h-conductor")
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Clear existing handlers to avoid duplicates on repeated calls
    logger.handlers.clear()

    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setLevel(getattr(logging, log_level, logging.INFO))

    if log_format == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(TextFormatter())

    logger.addHandler(handler)
    logger.propagate = False

    return logger
