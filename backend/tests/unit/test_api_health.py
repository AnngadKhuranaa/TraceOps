"""Unit tests for FastAPI health and readiness endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_health_endpoint(async_client: AsyncClient) -> None:
    """Verify root /health endpoint responds with 200 OK and expected structure."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "traceops-api"
    assert "X-Correlation-ID" in response.headers
    assert "X-Response-Time-Ms" in response.headers


@pytest.mark.asyncio
async def test_v1_health_endpoint(async_client: AsyncClient) -> None:
    """Verify /api/v1/health endpoint responds identically to root probe."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_readiness_endpoint_healthy(async_client: AsyncClient) -> None:
    """Verify /api/v1/ready responds 200 when backing services are operational."""
    response = await async_client.get("/api/v1/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["components"]["database"] == "healthy"


@pytest.mark.asyncio
async def test_readiness_endpoint_unhealthy_returns_503(unhealthy_client: AsyncClient) -> None:
    """Verify /api/v1/ready responds 503 Service Unavailable when database fails."""
    response = await unhealthy_client.get("/api/v1/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["code"] == "DATABASE_CONNECTION_ERROR"
    assert data["status"] == 503
    assert "correlation_id" in data
