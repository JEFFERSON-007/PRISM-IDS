"""Main FastAPI Application Entrypoint for PRISM IDS Server Foundation."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
import structlog

from app.api.ai_routes import router as ai_router
from app.api.v1.endpoints.websocket import router as ws_router
from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.exceptions import (
    PRISMBaseException,
    prism_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.logging import setup_logging
from app.database.base import Base
from app.database.session import check_database_health, engine
# Ensure all models are loaded into Base.metadata
import app.models  # noqa: F401
from app.middlewares.logging import RequestLoggingMiddleware
from app.middlewares.request_id import RequestIDMiddleware
from app.middlewares.security_headers import SecurityHeadersMiddleware
from app.middlewares.timing import TimingMiddleware
from fastapi.exceptions import RequestValidationError

# Setup structured logging
setup_logging()
logger = structlog.get_logger("prism_ids.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager handling startup and shutdown initialization."""
    logger.info(
        "Starting PRISM IDS Server Foundation",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )
    # Automatically create missing database tables at startup
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema tables verified and ready.")
    except Exception as db_err:
        logger.warning("Could not auto-create database tables", error=str(db_err))

    # Check DB connection readiness at startup
    db_health = await check_database_health()
    logger.info("Database connection status", db_status=db_health)

    yield

    logger.info("Shutting down PRISM IDS Server Foundation...")
    await engine.dispose()
    logger.info("Database engine connections closed successfully.")


def create_application() -> FastAPI:
    """FastAPI application factory configuring routes, middlewares, exceptions, and OpenAPI."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Predictive Reasoning and Intelligent Security Monitoring (PRISM IDS) "
            "Server Infrastructure Foundation API."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure Custom Middlewares (Order of execution: bottom to top for request, top to bottom for response)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_origin_regex=r"https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Correlation-ID", "X-Process-Time"],
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # Register Exception Handlers
    app.add_exception_handler(PRISMBaseException, prism_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # Mount API Routers
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)
    app.include_router(ai_router)
    app.include_router(ws_router)

    return app


app = create_application()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        log_config=None,  # Handled by structlog
    )
