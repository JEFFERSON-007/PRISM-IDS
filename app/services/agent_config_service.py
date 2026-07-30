"""Agent Configuration Management Service."""

from typing import Optional
import uuid
from app.core.exceptions import NotFoundError
from app.models.agent_config import AgentConfiguration
from app.repositories.agent_config_repository import AgentConfigRepository
from app.repositories.agent_repository import AgentRepository
from app.schemas.agent_config import AgentConfigUpdate
from app.services.audit_service import AuditService


class AgentConfigService:
    """Service synchronizing and updating agent parameters."""

    def __init__(
        self,
        config_repository: AgentConfigRepository,
        agent_repository: AgentRepository,
        audit_service: AuditService,
    ) -> None:
        self.config_repo = config_repository
        self.agent_repo = agent_repository
        self.audit_service = audit_service

    async def get_configuration(self, agent_id: uuid.UUID) -> AgentConfiguration:
        """Fetch configuration for an agent."""
        config = await self.config_repo.get_by_agent_id(agent_id)
        if not config:
            # Fallback check if agent exists
            agent = await self.agent_repo.get_by_id(agent_id)
            if not agent:
                raise NotFoundError(f"Agent with ID '{agent_id}' not found")
            # Create default configuration if missing
            default_cfg = AgentConfiguration(
                agent_id=agent_id,
                version=1,
                capture_interface="eth0",
                packet_filters="ip",
                log_level="INFO",
                sampling_rate=1.0,
            )
            config = await self.config_repo.create(default_cfg)
        return config

    async def update_configuration(
        self, agent_id: uuid.UUID, body: AgentConfigUpdate, modifier_id: Optional[uuid.UUID] = None
    ) -> AgentConfiguration:
        """Update agent parameters and increment configuration version."""
        config = await self.get_configuration(agent_id)
        update_data = body.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(config, field, value)

        config.version += 1
        updated = await self.config_repo.update(config)

        await self.audit_service.log_event(
            user_id=modifier_id,
            agent_id=agent_id,
            action="UPDATE_AGENT_CONFIG",
            resource=f"agent_config:{agent_id}",
            details={"new_version": updated.version, "updates": update_data},
        )
        return updated
