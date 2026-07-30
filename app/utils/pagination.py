"""Pagination Helpers."""

import math
from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PageParams(BaseModel):
    """Standardized request pagination query parameters."""

    page: int = Field(default=1, ge=1, description="Page number starting at 1")
    size: int = Field(default=20, ge=1, le=100, description="Items per page limit (max 100)")

    @property
    def offset(self) -> int:
        """Calculate SQL database query offset."""
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized paginated list response metadata envelope."""

    items: List[T]
    total: int
    page: int
    size: int
    total_pages: int

    @classmethod
    def create(cls, items: List[T], total: int, params: PageParams) -> "PaginatedResponse[T]":
        """Factory method constructing PaginatedResponse instance."""
        total_pages = math.ceil(total / params.size) if params.size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=params.page,
            size=params.size,
            total_pages=total_pages,
        )
