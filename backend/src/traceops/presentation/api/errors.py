"""Centralized exception handling adhering to RFC 7807 Problem Details."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from traceops.domain.exceptions import (
    ConfigurationError,
    DatabaseConnectionError,
    EntityNotFoundError,
    TraceOpsError,
)
from traceops.infrastructure.logging import correlation_id_ctx, get_logger

logger = get_logger(__name__)


def _build_problem_details(
    *,
    status_code: int,
    title: str,
    detail: str,
    code: str,
    instance: str,
    errors: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Construct an RFC 7807 compliant problem details dictionary."""
    problem: dict[str, Any] = {
        "type": f"https://traceops.dev/errors/{code.lower().replace('_', '-')}",
        "title": title,
        "status": status_code,
        "detail": detail,
        "code": code,
        "instance": instance,
        "correlation_id": correlation_id_ctx.get() or "unknown",
    }
    if errors:
        problem["errors"] = errors
    return problem


def register_error_handlers(app: FastAPI) -> None:
    """Register centralized exception handlers on the FastAPI application."""

    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(request: Request, exc: EntityNotFoundError) -> JSONResponse:
        problem = _build_problem_details(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Entity Not Found",
            detail=exc.message,
            code=exc.code,
            instance=request.url.path,
        )
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=problem)

    @app.exception_handler(DatabaseConnectionError)
    async def database_error_handler(
        request: Request, exc: DatabaseConnectionError
    ) -> JSONResponse:
        logger.error(f"Database connection error: {exc.message}", exc_info=True)
        problem = _build_problem_details(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            title="Service Unavailable",
            detail="Database service is unavailable or not accepting connections.",
            code=exc.code,
            instance=request.url.path,
        )
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=problem)

    @app.exception_handler(ConfigurationError)
    async def configuration_error_handler(
        request: Request, exc: ConfigurationError
    ) -> JSONResponse:
        logger.error(f"Configuration error: {exc.message}")
        problem = _build_problem_details(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            title="Configuration Error",
            detail="A system configuration error occurred.",
            code=exc.code,
            instance=request.url.path,
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=problem)

    @app.exception_handler(TraceOpsError)
    async def domain_error_handler(request: Request, exc: TraceOpsError) -> JSONResponse:
        logger.warning(f"Domain error occurred: {exc.message} ({exc.code})")
        problem = _build_problem_details(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Bad Request",
            detail=exc.message,
            code=exc.code,
            instance=request.url.path,
        )
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=problem)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        problem = _build_problem_details(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Validation Error",
            detail="Request validation failed for the given input.",
            code="VALIDATION_ERROR",
            instance=request.url.path,
            errors=[
                {"loc": err["loc"], "msg": err["msg"], "type": err["type"]} for err in exc.errors()
            ],
        )
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=problem)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        title = "HTTP Error"
        if exc.status_code == 404:
            title = "Not Found"
        elif exc.status_code == 405:
            title = "Method Not Allowed"

        problem = _build_problem_details(
            status_code=exc.status_code,
            title=title,
            detail=str(exc.detail),
            code=f"HTTP_{exc.status_code}",
            instance=request.url.path,
        )
        return JSONResponse(status_code=exc.status_code, content=problem)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.critical(f"Unhandled server exception: {exc}", exc_info=True)
        problem = _build_problem_details(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            title="Internal Server Error",
            detail="An unexpected error occurred. Please contact system administrator.",
            code="INTERNAL_SERVER_ERROR",
            instance=request.url.path,
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=problem)
