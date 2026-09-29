"""Integration tests for database migration execution."""

from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import text

from alembic import command
from traceops.infrastructure.config import Settings
from traceops.infrastructure.persistence.database import DatabaseSessionManager


def test_alembic_migrations() -> None:
    """Verify Alembic migrations can upgrade and downgrade successfully."""
    settings = Settings()
    backend_dir = Path(__file__).parent.parent.parent
    ini_path = backend_dir / "alembic.ini"

    if not ini_path.exists():
        pytest.fail(f"alembic.ini not found at {ini_path}")

    alembic_cfg = Config(str(ini_path))
    alembic_cfg.set_main_option("script_location", str(backend_dir / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)

    # Check if database is reachable before running migrations
    manager = DatabaseSessionManager()
    manager.init(settings)
    import asyncio

    is_alive = asyncio.run(manager.ping())
    asyncio.run(manager.close())

    if not is_alive:
        pytest.skip("PostgreSQL is not reachable; start via `docker compose up -d postgres`")

    # Run upgrade to head
    command.upgrade(alembic_cfg, "head")

    # Verify migration created the baseline table
    async def verify_table_exists() -> bool:
        m = DatabaseSessionManager()
        m.init(settings)
        try:
            async with m.session() as session:
                res = await session.execute(
                    text(
                        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '_traceops_metadata')"
                    )
                )
                return bool(res.scalar())
        finally:
            await m.close()

    assert asyncio.run(verify_table_exists()) is True
