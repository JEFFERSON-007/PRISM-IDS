"""Agent Management, Registration, Heartbeat, and Configuration APIs."""

from typing import List
import uuid
from fastapi import APIRouter, Depends, Query, Request, status
from app.api.dependencies import (
    get_agent_config_service,
    get_agent_service,
    get_authenticated_agent,
    get_current_user,
    get_heartbeat_service,
    require_permission,
)
from app.authentication.permissions import Permission
from app.models.agent import Agent
from app.models.user import User
from app.schemas.agent import (
    AgentRegisterRequest,
    AgentRegisterResponse,
    AgentResponse,
    AgentUpdateRequest,
)
from app.schemas.agent_config import AgentConfigResponse, AgentConfigUpdate
from app.schemas.heartbeat import HeartbeatCreate, HeartbeatResponse
from app.services.agent_config_service import AgentConfigService
from app.services.agent_service import AgentService
from app.services.heartbeat_service import HeartbeatService
from app.utils.pagination import PageParams, PaginatedResponse

router = APIRouter(prefix="/agents", tags=["Agent Management"])


@router.post(
    "/register",
    response_model=AgentRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New Agent",
    description="Onboard a new monitoring agent, issue cryptographic secret credentials, and create initial configuration.",
)
async def register_agent(
    body: AgentRegisterRequest,
    request: Request,
    agent_service: AgentService = Depends(get_agent_service),
) -> AgentRegisterResponse:
    """Register monitoring agent."""
    client_ip = request.client.host if request.client else None
    return await agent_service.register_agent(body, ip_address=client_ip)


@router.post(
    "/heartbeat",
    response_model=HeartbeatResponse,
    status_code=status.HTTP_200_OK,
    summary="Agent Heartbeat Telemetry",
    description="Submit periodic agent health telemetry (CPU, RAM, Disk, Network) authenticated via X-Agent-ID and X-Agent-Secret headers.",
)
async def submit_heartbeat(
    body: HeartbeatCreate,
    authenticated_agent: Agent = Depends(get_authenticated_agent),
    heartbeat_service: HeartbeatService = Depends(get_heartbeat_service),
) -> HeartbeatResponse:
    """Submit agent heartbeat telemetry."""
    heartbeat = await heartbeat_service.record_heartbeat(authenticated_agent.id, body)
    return HeartbeatResponse.model_validate(heartbeat)


@router.get(
    "",
    response_model=PaginatedResponse[AgentResponse],
    status_code=status.HTTP_200_OK,
    summary="List Agents",
    description="Fetch paginated list of registered monitoring agents and their live health status.",
    dependencies=[Depends(require_permission(Permission.READ_ALERTS))],
)
async def list_agents(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    agent_service: AgentService = Depends(get_agent_service),
    heartbeat_service: HeartbeatService = Depends(get_heartbeat_service),
) -> PaginatedResponse[AgentResponse]:
    """List agents and sweep offline status."""
    await heartbeat_service.detect_and_mark_offline_agents()
    params = PageParams(page=page, size=size)
    agents = await agent_service.list_agents(skip=params.offset, limit=params.size)
    total = len(agents)
    agent_dtos = [AgentResponse.model_validate(a) for a in agents]
    return PaginatedResponse.create(items=agent_dtos, total=total, params=params)


@router.get(
    "/{agent_id}",
    response_model=AgentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Agent Details",
    description="Fetch details and status for a specific monitoring agent.",
    dependencies=[Depends(require_permission(Permission.READ_ALERTS))],
)
async def get_agent_by_id(
    agent_id: uuid.UUID,
    agent_service: AgentService = Depends(get_agent_service),
) -> AgentResponse:
    """Fetch agent details."""
    agent = await agent_service.get_agent_by_id(agent_id)
    return AgentResponse.model_validate(agent)


@router.get(
    "/{agent_id}/configuration",
    response_model=AgentConfigResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Agent Configuration",
    description="Retrieve capture interface, packet filters, log level, and sampling configuration for an agent.",
)
async def get_agent_configuration(
    agent_id: uuid.UUID,
    config_service: AgentConfigService = Depends(get_agent_config_service),
) -> AgentConfigResponse:
    """Fetch agent configuration."""
    config = await config_service.get_configuration(agent_id)
    return AgentConfigResponse.model_validate(config)


@router.put(
    "/{agent_id}/configuration",
    response_model=AgentConfigResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Agent Configuration",
    description="Update operational parameters for an agent and bump configuration version.",
    dependencies=[Depends(require_permission(Permission.MANAGE_RULES))],
)
async def update_agent_configuration(
    agent_id: uuid.UUID,
    body: AgentConfigUpdate,
    current_user: User = Depends(get_current_user),
    config_service: AgentConfigService = Depends(get_agent_config_service),
) -> AgentConfigResponse:
    """Update agent configuration parameters."""
    config = await config_service.update_configuration(
        agent_id=agent_id, body=body, modifier_id=current_user.id
    )
    return AgentConfigResponse.model_validate(config)
