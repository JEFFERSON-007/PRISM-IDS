"""User Management API Endpoints."""

from typing import List
import uuid
from fastapi import APIRouter, Depends, Query, status
from app.api.dependencies import get_current_user, get_user_service, require_permission
from app.authentication.permissions import Permission
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.utils.pagination import PageParams, PaginatedResponse

router = APIRouter(prefix="/users", tags=["User Management"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User",
    description="Create a new user account with assigned role.",
    dependencies=[Depends(require_permission(Permission.WRITE_USERS))],
)
async def create_user(
    body: UserCreate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Create user account."""
    user = await user_service.create_user(body, creator_id=current_user.id)
    return UserResponse.model_validate(user)


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List Users",
    description="Fetch paginated list of active users.",
    dependencies=[Depends(require_permission(Permission.READ_USERS))],
)
async def list_users(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    user_service: UserService = Depends(get_user_service),
) -> PaginatedResponse[UserResponse]:
    """List users with pagination."""
    params = PageParams(page=page, size=size)
    users = await user_service.get_users(skip=params.offset, limit=params.size)
    total = len(users)  # Or count total in repo
    user_dtos = [UserResponse.model_validate(u) for u in users]
    return PaginatedResponse.create(items=user_dtos, total=total, params=params)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User Details",
    description="Retrieve user metadata by primary key UUID.",
    dependencies=[Depends(require_permission(Permission.READ_USERS))],
)
async def get_user_by_id(
    user_id: uuid.UUID,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Fetch user by ID."""
    user = await user_service.get_user_by_id(user_id)
    return UserResponse.model_validate(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update User Profile",
    description="Update user email, full name, role, or active status.",
    dependencies=[Depends(require_permission(Permission.WRITE_USERS))],
)
async def update_user(
    user_id: uuid.UUID,
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Update user account."""
    user = await user_service.update_user(user_id, body, modifier_id=current_user.id)
    return UserResponse.model_validate(user)


@router.put(
    "/{user_id}/disable",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Disable User Account",
    description="Deactivate a user account to revoke login permissions.",
    dependencies=[Depends(require_permission(Permission.DELETE_USERS))],
)
async def disable_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Disable user account."""
    user = await user_service.disable_user(user_id, modifier_id=current_user.id)
    return UserResponse.model_validate(user)
