"""Rate Limiting Middleware for Security Hardening."""

import time
from typing import Any, Dict, Tuple
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import structlog

logger = structlog.get_logger("prism_ids.rate_limiter")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory Token Bucket IP rate-limiting middleware."""

    def __init__(self, app: Any, requests_per_minute: int = 120) -> None:
        super().__init__(app)
        self.rpm = requests_per_minute
        # Storage: client_ip -> (request_count, window_start_time)
        self.ip_buckets: Dict[str, Tuple[int, float]] = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip static docs / openapi routes from rate limiting
        if request.url.path in ["/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()

        if client_ip in self.ip_buckets:
            count, window_start = self.ip_buckets[client_ip]
            if now - window_start < 60:
                if count >= self.rpm:
                    logger.warning("Rate limit exceeded for IP", client_ip=client_ip, count=count)
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={"detail": "Rate limit exceeded. Maximum 120 requests per minute allowed."},
                    )
                self.ip_buckets[client_ip] = (count + 1, window_start)
            else:
                # Reset 60s sliding window
                self.ip_buckets[client_ip] = (1, now)
        else:
            self.ip_buckets[client_ip] = (1, now)

        return await call_next(request)
