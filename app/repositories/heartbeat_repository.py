"""Heartbeat Repository Implementation."""

from typing import Optional, Sequence
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.heartbeat import Heartbeat
from app.repositories.base import BaseRepository


class HeartbeatRepository(BaseRepository[Heartbeat]):
    """Repository storing and querying periodic agent heartbeat records."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Heartbeat, session=session)

    async def get_latest_by_agent_id(self, agent_id: uuid.UUID) -> Optional[Heartbeat]:
        """Fetch latest heartbeat entry for an agent."""
        stmt = (
            select(Heartbeat)
            .where(Heartbeat.agent_id == agent_id)
            .order_by(Heartbeat.timestamp.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_history_by_agent_id(
        self, agent_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Sequence[Heartbeat]:
        """Fetch historical heatbeats for an agent ordered by timestamp descending."""
        stmt = (
            select(Heartbeat)
            .where(Heartbeat.agent_id == agent_id)
            .order_by(Heartbeat.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
