"""Dependency injection composition root."""

from fastapi import Depends

from traceops.application.ports.database import DatabaseHealthPort
from traceops.application.use_cases.check_health import HealthCheckUseCase
from traceops.infrastructure.config import Settings, get_settings
from traceops.infrastructure.persistence.database import DatabaseSessionManager, get_db_manager
from traceops.infrastructure.persistence.health_adapter import SqlAlchemyDatabaseHealthAdapter


def get_application_settings() -> Settings:
    """Dependency provider for application settings."""
    return get_settings()


def get_database_health_port(
    session_manager: DatabaseSessionManager = Depends(get_db_manager),
) -> DatabaseHealthPort:
    """Dependency provider for DatabaseHealthPort implementation."""
    return SqlAlchemyDatabaseHealthAdapter(session_manager)


def get_health_check_use_case(
    db_port: DatabaseHealthPort = Depends(get_database_health_port),
) -> HealthCheckUseCase:
    """Dependency provider for HealthCheckUseCase."""
    return HealthCheckUseCase(database_port=db_port)
