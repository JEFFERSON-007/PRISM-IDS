"""Agent Registration and Authentication Service."""

from datetime import datetime, timezone
import secrets
from typing import Optional, Sequence
import uuid
from app.authentication.password import hash_password, verify_password
from app.core.exceptions import AuthenticationError, PRISMValidationError, NotFoundError
from app.models.agent import Agent
from app.models.agent_config import AgentConfiguration
from app.repositories.agent_config_repository import AgentConfigRepository
from app.repositories.agent_repository import AgentRepository
from app.schemas.agent import AgentRegisterRequest, AgentRegisterResponse, AgentUpdateRequest
from app.services.audit_service import AuditService


class AgentService:
    """Service executing agent onboarding, authentication, and status management."""

    def __init__(
        self,
        agent_repository: AgentRepository,
        agent_config_repository: AgentConfigRepository,
        audit_service: AuditService,
    ) -> None:
        self.agent_repo = agent_repository
        self.config_repo = agent_config_repository
        self.audit_service = audit_service

    async def register_agent(
        self, request: AgentRegisterRequest, ip_address: Optional[str] = None
    ) -> AgentRegisterResponse:
        """Register a new monitoring agent, generate a secure secret key, and create default configuration."""
        existing = await self.agent_repo.get_by_name(request.agent_name)
        if existing:
            raise PRISMValidationError(f"Agent with name '{request.agent_name}' is already registered.")

        # Generate cryptographic secret key (32 bytes hex)
        raw_secret_key = f"prism_agent_{secrets.token_hex(24)}"
        secret_hash = hash_password(raw_secret_key)

        now = datetime.now(timezone.utc)
        agent = Agent(
            agent_name=request.agent_name,
            hostname=request.hostname,
            ip_address=request.ip_address,
            operating_system=request.operating_system,
            version=request.version,
            secret_key_hash=secret_hash,
            registration_time=now,
            is_online=True,
            health_status="healthy",
        )
        saved_agent = await self.agent_repo.create(agent)

        # Create default agent configuration
        default_config = AgentConfiguration(
            agent_id=saved_agent.id,
            version=1,
            capture_interface="eth0",
            packet_filters="ip",
            log_level="INFO",
            sampling_rate=1.0,
        )
        await self.config_repo.create(default_config)

        await self.audit_service.log_event(
            agent_id=saved_agent.id,
            action="AGENT_REGISTERED",
            resource=f"agent:{saved_agent.id}",
            ip_address=ip_address,
            details={"agent_name": saved_agent.agent_name, "hostname": saved_agent.hostname},
        )

        return AgentRegisterResponse(
            agent_id=saved_agent.id,
            agent_name=saved_agent.agent_name,
            secret_key=raw_secret_key,
            status="registered",
        )

    async def authenticate_agent(self, agent_id: uuid.UUID, secret_key: str) -> Agent:
        """Verify agent ID and secret key credentials."""
        agent = await self.agent_repo.get_by_id(agent_id)
        if not agent:
            raise AuthenticationError("Invalid Agent ID credentials")

        if not verify_password(secret_key, agent.secret_key_hash):
            raise AuthenticationError("Invalid Agent secret key credentials")

        return agent

    async def get_agent_by_id(self, agent_id: uuid.UUID) -> Agent:
        """Fetch agent by primary key."""
        agent = await self.agent_repo.get_by_id(agent_id)
        if not agent:
            raise NotFoundError(f"Agent with ID '{agent_id}' not found")
        return agent

    async def list_agents(self, skip: int = 0, limit: int = 100) -> Sequence[Agent]:
        """Fetch paginated list of monitoring agents."""
        return await self.agent_repo.get_all(skip=skip, limit=limit)

    async def update_agent(self, agent_id: uuid.UUID, obj_in: AgentUpdateRequest) -> Agent:
        """Update agent metadata or health status."""
        agent = await self.get_agent_by_id(agent_id)
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        return await self.agent_repo.update(agent)
