"""Database health adapter implementing application DatabaseHealthPort."""

from traceops.application.ports.database import DatabaseHealthPort
from traceops.infrastructure.persistence.database import DatabaseSessionManager


class SqlAlchemyDatabaseHealthAdapter(DatabaseHealthPort):
    """Verifies database connectivity using SQLAlchemy engine ping."""

    def __init__(self, session_manager: DatabaseSessionManager) -> None:
        self._session_manager = session_manager

    async def check_health(self) -> bool:
        """Probe the database to verify active connection."""
        return await self._session_manager.ping()
