"""Unit tests for centralized error handling and RFC 7807 problem details."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from traceops.domain.exceptions import EntityNotFoundError, TraceOpsError
from traceops.presentation.api.errors import register_error_handlers
from traceops.presentation.api.middleware import CorrelationIdMiddleware


@pytest.fixture
def error_test_app() -> FastAPI:
    """Create a minimal app with test endpoints that raise domain exceptions."""
    app = FastAPI()
    app.add_middleware(CorrelationIdMiddleware)
    register_error_handlers(app)

    @app.get("/trigger-not-found")
    def trigger_not_found() -> None:
        raise EntityNotFoundError(entity_type="Service", entity_id="srv_123")

    @app.get("/trigger-domain-error")
    def trigger_domain_error() -> None:
        raise TraceOpsError(message="Invalid calculation parameter.", code="INVALID_PARAM")

    @app.get("/trigger-unhandled")
    def trigger_unhandled() -> None:
        raise RuntimeError("Secret internal failure that must not leak")

    return app


@pytest.mark.asyncio
async def test_entity_not_found_mapping(error_test_app: FastAPI) -> None:
    """Verify EntityNotFoundError maps to RFC 7807 404 response."""
    transport = ASGITransport(app=error_test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/trigger-not-found")
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == 404
        assert data["code"] == "ENTITY_NOT_FOUND"
        assert "Service with id 'srv_123' not found." in data["detail"]
        assert "correlation_id" in data


@pytest.mark.asyncio
async def test_domain_error_mapping(error_test_app: FastAPI) -> None:
    """Verify generic TraceOpsError maps to RFC 7807 400 Bad Request."""
    transport = ASGITransport(app=error_test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/trigger-domain-error")
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == 400
        assert data["code"] == "INVALID_PARAM"


@pytest.mark.asyncio
async def test_unhandled_exception_does_not_leak_internals(error_test_app: FastAPI) -> None:
    """Verify unexpected exceptions return generic 500 without leaking stack traces or secrets."""
    transport = ASGITransport(app=error_test_app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/trigger-unhandled")
        assert response.status_code == 500
        data = response.json()
        assert data["status"] == 500
        assert data["code"] == "INTERNAL_SERVER_ERROR"
        # Verify the sensitive internal error message was not exposed
        assert "Secret internal failure" not in data["detail"]
        assert "correlation_id" in data
