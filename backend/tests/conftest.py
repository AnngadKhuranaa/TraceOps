"""Test configuration and shared fixtures."""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from traceops.application.ports.database import DatabaseHealthPort
from traceops.infrastructure.config import Settings
from traceops.presentation.api.app import create_app
from traceops.presentation.api.dependencies import get_database_health_port


class MockHealthyDatabasePort(DatabaseHealthPort):
    """Test double for healthy database connection."""

    async def check_health(self) -> bool:
        return True


class MockUnhealthyDatabasePort(DatabaseHealthPort):
    """Test double for failed database connection."""

    async def check_health(self) -> bool:
        return False


@pytest.fixture
def test_settings() -> Settings:
    """Provide isolated settings for testing."""
    return Settings(
        app_name="TraceOps Test API",
        app_env="test",
        debug=True,
        log_level="DEBUG",
        database_url="postgresql+asyncpg://postgres:postgres@localhost:5432/traceops_test",
    )


@pytest.fixture
async def async_client(test_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTP async test client with mock healthy database."""
    app = create_app(test_settings)
    app.dependency_overrides[get_database_health_port] = lambda: MockHealthyDatabasePort()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def unhealthy_client(test_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTP async test client with mock failing database."""
    app = create_app(test_settings)
    app.dependency_overrides[get_database_health_port] = lambda: MockUnhealthyDatabasePort()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
