"""Unit tests for HealthCheckUseCase."""

import pytest

from traceops.application.ports.database import DatabaseHealthPort
from traceops.application.use_cases.check_health import HealthCheckUseCase
from traceops.domain.exceptions import DatabaseConnectionError


class FakeHealthyPort(DatabaseHealthPort):
    async def check_health(self) -> bool:
        return True


class FakeUnhealthyPort(DatabaseHealthPort):
    async def check_health(self) -> bool:
        return False


def test_liveness_check() -> None:
    """Verify shallow liveness probe."""
    use_case = HealthCheckUseCase(database_port=FakeHealthyPort())
    result = use_case.check_liveness()
    assert result == {"status": "ok", "service": "traceops-api"}


@pytest.mark.asyncio
async def test_readiness_check_success() -> None:
    """Verify deep readiness probe when database is healthy."""
    use_case = HealthCheckUseCase(database_port=FakeHealthyPort())
    result = await use_case.check_readiness()
    assert result["status"] == "ready"
    assert result["components"]["database"] == "healthy"


@pytest.mark.asyncio
async def test_readiness_check_failure_raises_domain_error() -> None:
    """Verify deep readiness probe raises DatabaseConnectionError on probe failure."""
    use_case = HealthCheckUseCase(database_port=FakeUnhealthyPort())
    with pytest.raises(DatabaseConnectionError) as exc_info:
        await use_case.check_readiness()
    assert exc_info.value.code == "DATABASE_CONNECTION_ERROR"
