"""Backend entrypoint for ASGI servers."""

import uvicorn

from traceops.infrastructure.config import get_settings
from traceops.presentation.api.app import create_app

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "traceops.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
