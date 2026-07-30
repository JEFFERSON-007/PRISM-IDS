"""Agent Configuration Repository Implementation."""

from typing import Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agent_config import AgentConfiguration
from app.repositories.base import BaseRepository


class AgentConfigRepository(BaseRepository[AgentConfiguration]):
    """Repository storing and updating agent configurations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=AgentConfiguration, session=session)

    async def get_by_agent_id(self, agent_id: uuid.UUID) -> Optional[AgentConfiguration]:
        """Fetch configuration for an agent by agent_id."""
        stmt = select(AgentConfiguration).where(AgentConfiguration.agent_id == agent_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
