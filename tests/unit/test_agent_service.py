"""Unit tests for AgentService registration and credentials."""

from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest
from app.models.agent import Agent
from app.schemas.agent import AgentRegisterRequest
from app.services.agent_service import AgentService


@pytest.mark.asyncio
async def test_agent_registration_returns_credentials() -> None:
    """Test agent registration generates secret key."""
    agent_repo = MagicMock()
    agent_repo.get_by_name = AsyncMock(return_value=None)
    fake_id = uuid.uuid4()
    agent_repo.create = AsyncMock(
        return_value=Agent(
            id=fake_id,
            agent_name="agent-node-01",
            hostname="node01.prism.internal",
            ip_address="192.168.1.50",
            operating_system="Linux Ubuntu 22.04",
            version="1.0.0",
        )
    )

    config_repo = MagicMock()
    config_repo.create = AsyncMock()

    audit_service = MagicMock()
    audit_service.log_event = AsyncMock()

    service = AgentService(
        agent_repository=agent_repo,
        agent_config_repository=config_repo,
        audit_service=audit_service,
    )

    request = AgentRegisterRequest(
        agent_name="agent-node-01",
        hostname="node01.prism.internal",
        ip_address="192.168.1.50",
        operating_system="Linux Ubuntu 22.04",
        version="1.0.0",
    )

    result = await service.register_agent(request)
    assert result.agent_id == fake_id
    assert result.agent_name == "agent-node-01"
    assert result.secret_key.startswith("prism_agent_")
