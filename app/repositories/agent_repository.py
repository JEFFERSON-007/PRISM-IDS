"""Agent Repository Implementation."""

from datetime import datetime, timezone
from typing import Optional, Sequence
import uuid
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agent import Agent
from app.repositories.base import BaseRepository


class AgentRepository(BaseRepository[Agent]):
    """Repository handling database access for monitoring agents."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Agent, session=session)

    async def get_by_name(self, agent_name: str) -> Optional[Agent]:
        """Fetch agent by unique agent name."""
        stmt = select(Agent).where(Agent.agent_name == agent_name)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_hostname(self, hostname: str) -> Sequence[Agent]:
        """Fetch all agents running on a hostname."""
        stmt = select(Agent).where(Agent.hostname == hostname)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_heartbeat_status(
        self, agent_id: uuid.UUID, timestamp: datetime, health_status: str
    ) -> None:
        """Update last heartbeat timestamp, online status, and health status."""
        stmt = (
            update(Agent)
            .where(Agent.id == agent_id)
            .values(
                last_heartbeat=timestamp,
                is_online=True,
                health_status=health_status,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def mark_offline_inactive_agents(self, cutoff_time: datetime) -> int:
        """Mark agents offline if last_heartbeat is prior to cutoff_time."""
        stmt = (
            update(Agent)
            .where(
                Agent.is_online.is_(True),
                (Agent.last_heartbeat < cutoff_time) | (Agent.last_heartbeat.is_(None)),
            )
            .values(
                is_online=False,
                health_status="unhealthy",
                updated_at=datetime.now(timezone.utc),
            )
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount
