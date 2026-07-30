"""Request ID and Correlation ID Injection Middleware."""

import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import structlog

logger = structlog.get_logger("prism_ids.request_id")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to inject or extract X-Request-ID and X-Correlation-ID into request state and response headers."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        correlation_id = request.headers.get("X-Correlation-ID") or request_id

        # Bind to request state
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id

        # Bind contextvars for structlog logger
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            correlation_id=correlation_id,
        )

        response = await call_next(request)

        # Set headers on response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Correlation-ID"] = correlation_id

        structlog.contextvars.clear_contextvars()
        return response
