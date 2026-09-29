"""Health and readiness probe endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, status

from traceops.application.use_cases.check_health import HealthCheckUseCase
from traceops.presentation.api.dependencies import get_health_check_use_case

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Liveness Probe",
    description="Check whether the API service process is active.",
)
def get_health(
    use_case: HealthCheckUseCase = Depends(get_health_check_use_case),
) -> dict[str, str]:
    """Shallow liveness probe returning process status."""
    return use_case.check_liveness()


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness Probe",
    description="Check whether backing infrastructure components are connected and ready.",
)
async def get_ready(
    use_case: HealthCheckUseCase = Depends(get_health_check_use_case),
) -> dict[str, Any]:
    """Deep readiness probe verifying database connectivity."""
    return await use_case.check_readiness()
