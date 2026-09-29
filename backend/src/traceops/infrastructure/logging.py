"""Structured application logging with request correlation context."""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

# Context variable holding correlation ID for the active request/task
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")


class StructuredJsonFormatter(logging.Formatter):
    """Formats log records as structured single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add correlation ID if present in active context
        corr_id = correlation_id_ctx.get()
        if corr_id:
            log_data["correlation_id"] = corr_id

        # Include structured extra attributes if attached to record
        if hasattr(record, "extra_fields") and isinstance(record.extra_fields, dict):
            log_data.update(record.extra_fields)

        # Include exception trace if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class DevelopmentFormatter(logging.Formatter):
    """Human-readable formatted log output for local development."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(UTC).strftime("%H:%M:%S")
        corr_id = correlation_id_ctx.get()
        corr_suffix = f" [{corr_id}]" if corr_id else ""
        base = f"{timestamp} | {record.levelname:<7} | {record.name}{corr_suffix} - {record.getMessage()}"
        if record.exc_info:
            base += f"\n{self.formatException(record.exc_info)}"
        return base


def setup_logging(log_level: str = "INFO", app_env: str = "development") -> None:
    """Configure root and application loggers based on environment."""
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())

    # Clear existing handlers to prevent duplicate output
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    if app_env == "production":
        handler.setFormatter(StructuredJsonFormatter())
    else:
        handler.setFormatter(DevelopmentFormatter())

    root_logger.addHandler(handler)

    # Silence excessively verbose external loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a standard logger instance for the given module name."""
    return logging.getLogger(name)
