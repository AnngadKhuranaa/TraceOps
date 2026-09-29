"""API v1 endpoints package."""

from traceops.presentation.api.v1.endpoints.health import router as health_router

__all__ = ["health_router"]
