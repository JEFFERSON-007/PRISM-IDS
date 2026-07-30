"""Standardized API Error Response Schemas."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Detailed error object structure."""

    code: str = Field(example="AUTHENTICATION_ERROR")
    message: str = Field(example="Invalid or expired JWT token")
    details: Optional[Dict[str, Any]] = Field(default=None)


class ErrorResponse(BaseModel):
    """Envelope for all API error responses."""

    success: bool = Field(default=False, example=False)
    error: ErrorDetail
    request_id: Optional[str] = Field(default=None, example="req-12345")
