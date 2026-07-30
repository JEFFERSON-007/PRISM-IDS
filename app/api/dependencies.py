"""FastAPI Dependency Providers for Dependency Injection."""

from typing import AsyncGenerator, Callable, List, Optional
import uuid
from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from app.authentication.jwt import verify_token
from app.authentication.permissions import Permission as PermissionEnum, has_permission
from app.authentication.roles import Role as RoleEnum
from app.core.config import Settings, settings
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.database.session import get_db_session
from app.models.agent import Agent
from app.models.user import User
from app.repositories.agent_config_repository import AgentConfigRepository
from app.repositories.agent_repository import AgentRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.heartbeat_repository import HeartbeatRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.token import TokenData
from app.services.agent_config_service import AgentConfigService
from app.services.agent_service import AgentService
from app.services.audit_service import AuditService
from app.services.auth_service import AuthenticationService
from app.services.heartbeat_service import HeartbeatService
from app.services.role_service import RoleService
from app.services.user_service import UserService

security_bearer = HTTPBearer(auto_error=False)


def get_settings() -> Settings:
    """Dependency providing global settings instance."""
    return settings


def get_logger(request: Request) -> structlog.stdlib.BoundLogger:
    """Dependency providing contextual request logger."""
    request_id = getattr(request.state, "request_id", None)
    return structlog.get_logger("prism_ids.api").bind(request_id=request_id)


# Repository Injection Providers
def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(session=session)


def get_role_repository(session: AsyncSession = Depends(get_db_session)) -> RoleRepository:
    return RoleRepository(session=session)


def get_agent_repository(session: AsyncSession = Depends(get_db_session)) -> AgentRepository:
    return AgentRepository(session=session)


def get_heartbeat_repository(session: AsyncSession = Depends(get_db_session)) -> HeartbeatRepository:
    return HeartbeatRepository(session=session)


def get_agent_config_repository(session: AsyncSession = Depends(get_db_session)) -> AgentConfigRepository:
    return AgentConfigRepository(session=session)


def get_audit_repository(session: AsyncSession = Depends(get_db_session)) -> AuditRepository:
    return AuditRepository(session=session)


# Service Injection Providers
def get_audit_service(audit_repo: AuditRepository = Depends(get_audit_repository)) -> AuditService:
    return AuditService(audit_repository=audit_repo)


def get_role_service(role_repo: RoleRepository = Depends(get_role_repository)) -> RoleService:
    return RoleService(role_repository=role_repo)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    role_repo: RoleRepository = Depends(get_role_repository),
    audit_service: AuditService = Depends(get_audit_service),
) -> UserService:
    return UserService(user_repository=user_repo, role_repository=role_repo, audit_service=audit_service)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    audit_service: AuditService = Depends(get_audit_service),
) -> AuthenticationService:
    return AuthenticationService(user_repository=user_repo, audit_service=audit_service)


def get_agent_service(
    agent_repo: AgentRepository = Depends(get_agent_repository),
    config_repo: AgentConfigRepository = Depends(get_agent_config_repository),
    audit_service: AuditService = Depends(get_audit_service),
) -> AgentService:
    return AgentService(
        agent_repository=agent_repo, agent_config_repository=config_repo, audit_service=audit_service
    )


def get_heartbeat_service(
    hb_repo: HeartbeatRepository = Depends(get_heartbeat_repository),
    agent_repo: AgentRepository = Depends(get_agent_repository),
    audit_service: AuditService = Depends(get_audit_service),
) -> HeartbeatService:
    return HeartbeatService(
        heartbeat_repository=hb_repo, agent_repository=agent_repo, audit_service=audit_service
    )


def get_agent_config_service(
    config_repo: AgentConfigRepository = Depends(get_agent_config_repository),
    agent_repo: AgentRepository = Depends(get_agent_repository),
    audit_service: AuditService = Depends(get_audit_service),
) -> AgentConfigService:
    return AgentConfigService(
        config_repository=config_repo, agent_repository=agent_repo, audit_service=audit_service
    )


# Authentication & RBAC Dependencies
async def get_current_token_data(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
) -> TokenData:
    """Dependency verifying Bearer JWT access token."""
    if not credentials or not credentials.credentials:
        raise AuthenticationError("Authorization header with Bearer token is required")

    payload = verify_token(credentials.credentials, expected_type="access")
    username = payload.get("sub")
    role_str = payload.get("role", RoleEnum.ANALYST.value)
    permissions = payload.get("permissions", [])

    try:
        role = RoleEnum(role_str)
    except ValueError:
        role = RoleEnum.ANALYST

    return TokenData(username=username, role=role, permissions=permissions)


async def get_current_user(
    token_data: TokenData = Depends(get_current_token_data),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    """Dependency looking up active User entity in DB."""
    if not token_data.username:
        raise AuthenticationError("Invalid token subject payload")

    user = await user_repo.get_by_username(token_data.username)
    if not user or not user.is_active or user.deleted_at is not None:
        raise AuthenticationError("User is inactive or no longer exists")
    return user


def require_role(allowed_roles: List[RoleEnum]) -> Callable[..., TokenData]:
    """Dependency factory checking whether the current user holds one of the specified allowed roles."""

    async def role_checker(token_data: TokenData = Depends(get_current_token_data)) -> TokenData:
        if token_data.role not in allowed_roles:
            raise PermissionDeniedError(
                f"Role '{token_data.role}' is not authorized to access this resource"
            )
        return token_data

    return role_checker


def require_permission(required_permission: PermissionEnum) -> Callable[..., TokenData]:
    """Dependency factory checking whether the current user holds a specific granular permission."""

    async def permission_checker(token_data: TokenData = Depends(get_current_token_data)) -> TokenData:
        if not token_data.role or not has_permission(token_data.role, required_permission):
            raise PermissionDeniedError(
                f"Permission '{required_permission.value}' is required for this operation"
            )
        return token_data

    return permission_checker


# Agent Security Header Authentication Dependency
async def get_authenticated_agent(
    x_agent_id: Optional[str] = Header(None, alias="X-Agent-ID"),
    x_agent_secret: Optional[str] = Header(None, alias="X-Agent-Secret"),
    agent_service: AgentService = Depends(get_agent_service),
) -> Agent:
    """Dependency authenticating an agent via X-Agent-ID and X-Agent-Secret request headers."""
    if not x_agent_id or not x_agent_secret:
        raise AuthenticationError("X-Agent-ID and X-Agent-Secret authentication headers are required")

    try:
        agent_uuid = uuid.UUID(x_agent_id)
    except ValueError:
        raise AuthenticationError("Invalid X-Agent-ID header format")

    return await agent_service.authenticate_agent(agent_uuid, x_agent_secret)
