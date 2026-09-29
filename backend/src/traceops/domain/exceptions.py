"""Pure domain exceptions for TraceOps.

These exceptions have zero external framework dependencies (no FastAPI, no SQLAlchemy).
"""


class TraceOpsError(Exception):
    """Base exception for all domain and application errors in TraceOps."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class EntityNotFoundError(TraceOpsError):
    """Raised when an entity is not found."""

    def __init__(self, entity_type: str, entity_id: str) -> None:
        super().__init__(
            f"{entity_type} with id '{entity_id}' not found.",
            code="ENTITY_NOT_FOUND",
        )
        self.entity_type = entity_type
        self.entity_id = entity_id


class ConfigurationError(TraceOpsError):
    """Raised when configuration values are missing or invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="CONFIGURATION_ERROR")


class DatabaseConnectionError(TraceOpsError):
    """Raised when the database connection fails."""

    def __init__(self, message: str = "Database connection failed.") -> None:
        super().__init__(message, code="DATABASE_CONNECTION_ERROR")
