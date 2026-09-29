"""Integration tests for PostgreSQL database connectivity and session lifecycle."""

import pytest
from sqlalchemy import text

from traceops.infrastructure.config import Settings
from traceops.infrastructure.persistence.database import DatabaseSessionManager


@pytest.mark.asyncio
async def test_database_connection_and_query() -> None:
    """Verify actual database connectivity against PostgreSQL."""
    settings = Settings()
    manager = DatabaseSessionManager()
    manager.init(settings)

    try:
        is_alive = await manager.ping()
        if not is_alive:
            pytest.skip("PostgreSQL is not reachable; start via `docker compose up -d postgres`")

        async with manager.session() as session:
            result = await session.execute(text("SELECT 1 + 1 AS sum"))
            assert result.scalar() == 2
    finally:
        await manager.close()
