"""Structured Request and Response Logging Middleware."""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import structlog

logger = structlog.get_logger("prism_ids.http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware logging incoming requests and outgoing HTTP response details."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_host = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        logger.info(
            "HTTP Request Received",
            method=method,
            path=path,
            client_host=client_host,
            user_agent=request.headers.get("User-Agent", "unknown"),
        )

        response = await call_next(request)
        process_time_ms = getattr(request.state, "process_time_ms", 0.0)

        logger.info(
            "HTTP Response Sent",
            method=method,
            path=path,
            status_code=response.status_code,
            process_time_ms=process_time_ms,
        )

        return response
