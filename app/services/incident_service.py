"""Incident Lifecycle Management Service."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from app.models.incident import Incident
from app.repositories.incident_repository import IncidentRepository
from app.schemas.incident import (
    IncidentCreate,
    IncidentNoteCreate,
    IncidentPaginationResponse,
    IncidentRead,
)
from app.websocket.manager import ws_manager

logger = structlog.get_logger("prism_ids.incident_service")


class IncidentService:
    """Service handling security incident management workflows."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.incident_repo = IncidentRepository(session)

    async def create_incident(self, incident_in: IncidentCreate, creator_username: Optional[str] = None) -> IncidentRead:
        """Create a new security incident record."""
        inc_count = await self.incident_repo.get_open_count()
        gen_incident_id = f"INC-{datetime.now(timezone.utc).year}-{inc_count + 1:04d}"

        notes = []
        if creator_username:
            notes.append({
                "author": creator_username,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "note": f"Incident created by {creator_username}",
            })

        incident_orm = Incident(
            incident_id=gen_incident_id,
            title=incident_in.title,
            description=incident_in.description,
            severity=incident_in.severity.upper(),
            status="OPEN",
            assigned_to_user_id=incident_in.assigned_to_user_id,
            notes=notes,
            correlation_id=incident_in.correlation_id,
        )

        await self.incident_repo.create(incident_orm)
        await self.session.commit()
        await self.session.refresh(incident_orm)

        logger.info("Created security incident", incident_id=gen_incident_id, severity=incident_orm.severity)

        # Broadcast event
        read_dto = IncidentRead.model_validate(incident_orm)
        await ws_manager.broadcast({
            "type": "INCIDENT_UPDATE",
            "action": "CREATED",
            "incident": read_dto.model_dump(mode="json"),
        })

        return read_dto

    async def get_incidents_paginated(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        assigned_to_user_id: Optional[uuid.UUID] = None,
        search_query: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> IncidentPaginationResponse:
        """Query incidents with pagination."""
        items, total_records, total_pages = await self.incident_repo.filter_incidents(
            status=status,
            severity=severity,
            assigned_to_user_id=assigned_to_user_id,
            search_query=search_query,
            page=page,
            page_size=page_size,
        )

        read_items = [IncidentRead.model_validate(item) for item in items]
        return IncidentPaginationResponse(
            items=read_items,
            page=page,
            page_size=page_size,
            total_records=total_records,
            total_pages=total_pages,
        )

    async def get_incident_by_id(self, incident_id_or_uuid: str) -> Optional[IncidentRead]:
        """Fetch incident by string ID or UUID."""
        incident = await self.incident_repo.get_by_incident_id(incident_id_or_uuid)
        if not incident:
            try:
                u_id = uuid.UUID(incident_id_or_uuid)
                incident = await self.incident_repo.get_by_id(u_id)
            except ValueError:
                pass

        if not incident:
            return None
        return IncidentRead.model_validate(incident)

    async def update_status(self, incident_id: str, new_status: str, username: Optional[str] = None) -> Optional[IncidentRead]:
        """Update incident status (OPEN, ACKNOWLEDGED, RESOLVED, REOPENED)."""
        incident = await self.incident_repo.get_by_incident_id(incident_id)
        if not incident:
            return None

        old_status = incident.status
        incident.status = new_status.upper()
        incident.updated_at = datetime.now(timezone.utc)

        notes = incident.notes or []
        notes.append({
            "author": username or "System",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Status changed from {old_status} to {new_status.upper()}",
        })
        incident.notes = notes

        await self.session.commit()
        await self.session.refresh(incident)

        read_dto = IncidentRead.model_validate(incident)
        await ws_manager.broadcast({
            "type": "INCIDENT_UPDATE",
            "action": "STATUS_CHANGED",
            "incident": read_dto.model_dump(mode="json"),
        })

        return read_dto

    async def assign_analyst(self, incident_id: str, user_id: uuid.UUID, username: Optional[str] = None) -> Optional[IncidentRead]:
        """Assign analyst to incident."""
        incident = await self.incident_repo.get_by_incident_id(incident_id)
        if not incident:
            return None

        incident.assigned_to_user_id = user_id
        incident.updated_at = datetime.now(timezone.utc)

        notes = incident.notes or []
        notes.append({
            "author": username or "System",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Assigned incident to user {user_id}",
        })
        incident.notes = notes

        await self.session.commit()
        await self.session.refresh(incident)

        read_dto = IncidentRead.model_validate(incident)
        await ws_manager.broadcast({
            "type": "INCIDENT_UPDATE",
            "action": "ASSIGNED",
            "incident": read_dto.model_dump(mode="json"),
        })

        return read_dto

    async def add_note(self, incident_id: str, note_text: str, username: str) -> Optional[IncidentRead]:
        """Add investigation note to incident."""
        incident = await self.incident_repo.get_by_incident_id(incident_id)
        if not incident:
            return None

        notes = incident.notes or []
        notes.append({
            "author": username,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": note_text,
        })
        incident.notes = notes
        incident.updated_at = datetime.now(timezone.utc)

        await self.session.commit()
        await self.session.refresh(incident)

        read_dto = IncidentRead.model_validate(incident)
        return read_dto
