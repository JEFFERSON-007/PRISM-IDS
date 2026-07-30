"""Centralized Exception Hierarchy and FastAPI Error Handlers."""

from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger("prism_ids.exceptions")


class PRISMBaseException(Exception):
    """Base exception class for all PRISM IDS application errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class PRISMValidationError(PRISMBaseException):
    """Raised when request or domain validation fails."""

    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class AuthenticationError(PRISMBaseException):
    """Raised when authentication fails or JWT is invalid/expired."""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class PermissionDeniedError(PRISMBaseException):
    """Raised when an authenticated user lacks permissions."""

    def __init__(self, message: str = "Permission denied", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class NotFoundError(PRISMBaseException):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class DatabaseError(PRISMBaseException):
    """Raised when database query or connection operations fail."""

    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


def build_error_response(
    status_code: int,
    code: str,
    message: str,
    request_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """Build a standardized JSON error response."""
    payload = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
        "request_id": request_id,
    }
    return JSONResponse(status_code=status_code, content=payload)


async def prism_exception_handler(request: Request, exc: PRISMBaseException) -> JSONResponse:
    """Handler for all PRISM internal exceptions."""
    request_id = getattr(request.state, "request_id", None)
    logger.error(
        "Application exception caught",
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        request_id=request_id,
        path=request.url.path,
    )
    return build_error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        request_id=request_id,
        details=exc.details,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler for FastAPI Pydantic request validation errors."""
    request_id = getattr(request.state, "request_id", None)
    logger.warning(
        "Request validation error",
        errors=exc.errors(),
        request_id=request_id,
        path=request.url.path,
    )
    return build_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="VALIDATION_ERROR",
        message="Request parameters or body validation failed",
        request_id=request_id,
        details={"validation_errors": exc.errors()},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global catch-all handler for unhandled unexpected exceptions."""
    request_id = getattr(request.state, "request_id", None)
    logger.critical(
        "Unhandled exception occurred",
        error=str(exc),
        exc_info=True,
        request_id=request_id,
        path=request.url.path,
    )
    return build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected server error occurred",
        request_id=request_id,
    )
