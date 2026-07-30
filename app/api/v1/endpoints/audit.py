"""Security Audit Logs API Endpoint."""

from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from app.api.dependencies import get_audit_service, require_permission
from app.authentication.permissions import Permission
from app.schemas.audit_log import AuditLogResponse
from app.services.audit_service import AuditService
from app.utils.pagination import PageParams, PaginatedResponse

router = APIRouter(prefix="/audit-logs", tags=["Audit & Compliance"])


@router.get(
    "",
    response_model=PaginatedResponse[AuditLogResponse],
    status_code=status.HTTP_200_OK,
    summary="Search Audit Logs",
    description="Query historical audit logs filtered by user, agent, action, or resource.",
    dependencies=[Depends(require_permission(Permission.READ_METRICS))],
)
async def search_audit_logs(
    user_id: Optional[uuid.UUID] = Query(None),
    agent_id: Optional[uuid.UUID] = Query(None),
    action: Optional[str] = Query(None),
    resource: Optional[str] = Query(None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    audit_service: AuditService = Depends(get_audit_service),
) -> PaginatedResponse[AuditLogResponse]:
    """Search audit logs."""
    params = PageParams(page=page, size=size)
    logs = await audit_service.get_logs(
        user_id=user_id,
        agent_id=agent_id,
        action=action,
        resource=resource,
        skip=params.offset,
        limit=params.size,
    )
    total = len(logs)
    log_dtos = [AuditLogResponse.model_validate(l) for l in logs]
    return PaginatedResponse.create(items=log_dtos, total=total, params=params)
