"""Audit Log Repository Implementation."""

from typing import Optional, Sequence
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    """Repository storing and querying audit log records."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=AuditLog, session=session)

    async def search_logs(
        self,
        user_id: Optional[uuid.UUID] = None,
        agent_id: Optional[uuid.UUID] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[AuditLog]:
        """Query audit log entries using optional filters ordered by timestamp descending."""
        stmt = select(AuditLog)
        if user_id:
            stmt = stmt.where(AuditLog.user_id == user_id)
        if agent_id:
            stmt = stmt.where(AuditLog.agent_id == agent_id)
        if action:
            stmt = stmt.where(AuditLog.action == action)
        if resource:
            stmt = stmt.where(AuditLog.resource == resource)

        stmt = stmt.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
