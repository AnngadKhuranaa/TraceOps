"""Domain layer for TraceOps. Pure Python dataclasses, entities, and domain exceptions."""

from traceops.domain.exceptions import (
    ConfigurationError,
    DatabaseConnectionError,
    EntityNotFoundError,
    TraceOpsError,
)

__all__ = [
    "ConfigurationError",
    "DatabaseConnectionError",
    "EntityNotFoundError",
    "TraceOpsError",
]
