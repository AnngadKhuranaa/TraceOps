"""FastAPI application factory for TraceOps."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from traceops import __version__
from traceops.infrastructure.config import Settings, get_settings
from traceops.infrastructure.logging import get_logger, setup_logging
from traceops.infrastructure.persistence.database import db_manager
from traceops.presentation.api.errors import register_error_handlers
from traceops.presentation.api.middleware import CorrelationIdMiddleware
from traceops.presentation.api.v1.endpoints.health import router as root_health_router
from traceops.presentation.api.v1.router import v1_router

logger = get_logger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure a FastAPI application instance."""
    app_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
        # Startup phase
        setup_logging(log_level=app_settings.log_level, app_env=app_settings.app_env)
        logger.info(f"Starting {app_settings.app_name} v{__version__} [env={app_settings.app_env}]")
        db_manager.init(app_settings)
        yield
        # Shutdown phase
        logger.info(f"Shutting down {app_settings.app_name}...")
        await db_manager.close()
        logger.info("Shutdown complete.")

    app = FastAPI(
        title=app_settings.app_name,
        version=__version__,
        description="Cloud incident investigation and root-cause intelligence platform API",
        docs_url="/docs" if app_settings.debug or app_settings.app_env != "production" else None,
        redoc_url="/redoc" if app_settings.debug or app_settings.app_env != "production" else None,
        openapi_url="/openapi.json"
        if app_settings.debug or app_settings.app_env != "production"
        else None,
        lifespan=lifespan,
    )

    # State
    app.state.settings = app_settings

    # Middleware
    app.add_middleware(CorrelationIdMiddleware)
    if app_settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=app_settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Register centralized RFC 7807 error handlers
    register_error_handlers(app)

    # Root health routes (for container probes and load balancers)
    app.include_router(root_health_router)

    # Versioned API routes
    app.include_router(v1_router)

    return app
