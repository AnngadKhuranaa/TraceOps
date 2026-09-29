"""API v1 master router."""

from fastapi import APIRouter

from traceops.presentation.api.v1.endpoints.health import router as health_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(health_router)
