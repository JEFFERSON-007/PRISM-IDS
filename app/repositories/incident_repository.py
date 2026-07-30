"""Incident Database Repository."""

import math

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import uuid
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.incident import Incident
from app.repositories.base import BaseRepository


class IncidentRepository(BaseRepository[Incident]):
    """Repository handling database operations for Incident Management."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Incident, session)

    async def get_by_incident_id(self, incident_id: str) -> Optional[Incident]:
        """Fetch incident by string identifier (e.g. INC-2026-001)."""
        stmt = select(Incident).where(Incident.incident_id == incident_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def filter_incidents(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        assigned_to_user_id: Optional[uuid.UUID] = None,
        search_query: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Incident], int, int]:
        """Query incidents with filtering and pagination."""
        stmt = select(Incident)
        count_stmt = select(func.count(Incident.id))

        filters = []
        if status:
            filters.append(Incident.status == status.upper())
        if severity:
            filters.append(Incident.severity == severity.upper())
        if assigned_to_user_id:
            filters.append(Incident.assigned_to_user_id == assigned_to_user_id)

        if search_query:
            pattern = f"%{search_query}%"
            filters.append(
                (Incident.title.ilike(pattern))
                | (Incident.description.ilike(pattern))
                | (Incident.incident_id.ilike(pattern))
                | (Incident.correlation_id.ilike(pattern))
            )

        if filters:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)

        total_res = await self.session.execute(count_stmt)
        total_records = total_res.scalar() or 0

        stmt = stmt.order_by(Incident.created_at.desc())
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        total_pages = math.ceil(total_records / page_size) if page_size > 0 else 1

        return items, total_records, total_pages

    async def get_open_count(self) -> int:
        """Count total open/active incidents."""
        stmt = select(func.count(Incident.id)).where(Incident.status.in_(["OPEN", "ACKNOWLEDGED", "REOPENED"]))
        res = await self.session.execute(stmt)
        return res.scalar() or 0
