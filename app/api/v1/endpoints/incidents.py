"""Incident Management REST API Endpoints."""

from typing import Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.incident import (
    IncidentAssignUpdate,
    IncidentCreate,
    IncidentNoteCreate,
    IncidentPaginationResponse,
    IncidentRead,
    IncidentStatusUpdate,
)
from app.services.incident_service import IncidentService

router = APIRouter(prefix="/incidents", tags=["Incidents"])
logger = structlog.get_logger("prism_ids.incidents_api")


@router.get("", response_model=IncidentPaginationResponse)
async def list_incidents(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: OPEN, ACKNOWLEDGED, RESOLVED, REOPENED"),
    severity: Optional[str] = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL"),
    assigned_to_user_id: Optional[uuid.UUID] = Query(None, description="Filter by assigned analyst user UUID"),
    search: Optional[str] = Query(None, description="Full text search across title, description, incident ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IncidentPaginationResponse:
    """Query, filter, and paginate security incidents (Requires JWT Auth)."""
    service = IncidentService(db)
    return await service.get_incidents_paginated(
        status=status_filter,
        severity=severity,
        assigned_to_user_id=assigned_to_user_id,
        search_query=search,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_in: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IncidentRead:
    """Create a new security incident (Requires JWT Auth)."""
    service = IncidentService(db)
    return await service.create_incident(incident_in, creator_username=current_user.username)


@router.get("/{incident_id}", response_model=IncidentRead)
async def get_incident_details(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IncidentRead:
    """Fetch incident details by incident_id (Requires JWT Auth)."""
    service = IncidentService(db)
    incident = await service.get_incident_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return incident


@router.put("/{incident_id}/status", response_model=IncidentRead)
async def update_incident_status(
    incident_id: str,
    status_in: IncidentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IncidentRead:
    """Update incident status: OPEN -> ACKNOWLEDGED -> RESOLVED -> REOPENED (Requires JWT Auth)."""
    service = IncidentService(db)
    updated = await service.update_status(incident_id, status_in.status, username=current_user.username)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return updated


@router.put("/{incident_id}/assign", response_model=IncidentRead)
async def assign_analyst_to_incident(
    incident_id: str,
    assign_in: IncidentAssignUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IncidentRead:
    """Assign an analyst to an incident (Requires JWT Auth)."""
    service = IncidentService(db)
    updated = await service.assign_analyst(incident_id, assign_in.assigned_to_user_id, username=current_user.username)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return updated


@router.post("/{incident_id}/notes", response_model=IncidentRead)
async def add_incident_note(
    incident_id: str,
    note_in: IncidentNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IncidentRead:
    """Add an investigation note to an incident (Requires JWT Auth)."""
    service = IncidentService(db)
    updated = await service.add_note(incident_id, note_in.note, username=current_user.username)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return updated
