"""API Response Builders."""

from typing import Any, Optional
from fastapi.responses import JSONResponse
from fastapi import status


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK,
    request_id: Optional[str] = None,
) -> JSONResponse:
    """Construct a standardized JSON success response."""
    payload = {
        "success": True,
        "message": message,
        "data": data,
        "request_id": request_id,
    }
    return JSONResponse(status_code=status_code, content=payload)


def error_response(
    code: str,
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    details: Any = None,
    request_id: Optional[str] = None,
) -> JSONResponse:
    """Construct a standardized JSON error response."""
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
