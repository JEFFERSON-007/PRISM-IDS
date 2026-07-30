"""Pydantic Schemas for Incident Management."""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


class IncidentCreate(BaseModel):
    """Schema for creating a security incident."""

    title: str = Field(min_length=3, max_length=255)
    description: Optional[str] = None
    severity: str = "MEDIUM"
    assigned_to_user_id: Optional[uuid.UUID] = None
    correlation_id: Optional[str] = None


class IncidentStatusUpdate(BaseModel):
    """Schema for updating incident status."""

    status: str = Field(description="OPEN, ACKNOWLEDGED, RESOLVED, or REOPENED")


class IncidentAssignUpdate(BaseModel):
    """Schema for assigning an analyst to an incident."""

    assigned_to_user_id: uuid.UUID


class IncidentNoteCreate(BaseModel):
    """Schema for adding an investigation note."""

    note: str = Field(min_length=1, max_length=2000)


class IncidentRead(BaseModel):
    """Schema for incident response payload."""

    id: uuid.UUID
    incident_id: str
    title: str
    description: Optional[str] = None
    severity: str
    status: str
    assigned_to_user_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    notes: Optional[List[Dict[str, Any]]] = None
    correlation_id: Optional[str] = None

    class Config:
        from_attributes = True


class IncidentPaginationResponse(BaseModel):
    """Paginated list of incidents."""

    items: List[IncidentRead]
    page: int
    page_size: int
    total_records: int
    total_pages: int
