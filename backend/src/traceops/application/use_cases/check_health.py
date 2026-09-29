"""Health check use cases orchestrating system liveness and readiness."""

from typing import Any

from traceops.application.ports.database import DatabaseHealthPort
from traceops.domain.exceptions import DatabaseConnectionError


class HealthCheckUseCase:
    """Orchestrates system liveness and readiness probes."""

    def __init__(self, database_port: DatabaseHealthPort) -> None:
        self._database_port = database_port

    def check_liveness(self) -> dict[str, str]:
        """Verify the service process is alive and responsive."""
        return {
            "status": "ok",
            "service": "traceops-api",
        }

    async def check_readiness(self) -> dict[str, Any]:
        """Verify essential backing infrastructure is connected and operational.

        Raises:
            DatabaseConnectionError: If database health check fails.
        """
        is_db_healthy = await self._database_port.check_health()
        if not is_db_healthy:
            raise DatabaseConnectionError("Database ping failed or timed out.")

        return {
            "status": "ready",
            "service": "traceops-api",
            "components": {
                "database": "healthy",
            },
        }
