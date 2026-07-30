"""Roles and Permissions API Endpoints."""

from typing import List
from fastapi import APIRouter, Depends, status
from app.api.dependencies import get_role_service, require_permission
from app.authentication.permissions import Permission as PermissionEnum
from app.schemas.role import PermissionResponse, RoleResponse
from app.services.role_service import RoleService

router = APIRouter(prefix="/roles", tags=["Role-Based Access Control"])


@router.get(
    "",
    response_model=List[RoleResponse],
    status_code=status.HTTP_200_OK,
    summary="List Roles",
    description="Fetch all registered system roles and their assigned permissions.",
    dependencies=[Depends(require_permission(PermissionEnum.READ_USERS))],
)
async def list_roles(
    role_service: RoleService = Depends(get_role_service),
) -> List[RoleResponse]:
    """Fetch system roles."""
    roles = await role_service.get_all_roles()
    return [RoleResponse.model_validate(r) for r in roles]


@router.get(
    "/permissions",
    response_model=List[PermissionResponse],
    status_code=status.HTTP_200_OK,
    summary="List Permissions",
    description="Fetch all fine-grained system permission capabilities.",
    dependencies=[Depends(require_permission(PermissionEnum.READ_USERS))],
)
async def list_permissions(
    role_service: RoleService = Depends(get_role_service),
) -> List[PermissionResponse]:
    """Fetch fine-grained permissions."""
    permissions = await role_service.get_all_permissions()
    return [PermissionResponse.model_validate(p) for p in permissions]
