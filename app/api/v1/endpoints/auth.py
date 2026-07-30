"""Authentication API Endpoints."""

from fastapi import APIRouter, Depends, Request, status
from app.api.dependencies import get_auth_service, get_current_user, get_user_service
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse
from app.schemas.user import PasswordChangeRequest, UserResponse
from app.services.auth_service import AuthenticationService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user credentials and issue signed JWT access and refresh token pair.",
)
async def login(
    body: LoginRequest,
    request: Request,
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> TokenResponse:
    """Authenticate username and password."""
    client_ip = request.client.host if request.client else None
    return await auth_service.authenticate_user(body, ip_address=client_ip)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Access Token",
    description="Issue a new JWT access and refresh token pair using a valid refresh token.",
)
async def refresh_token(
    body: RefreshTokenRequest,
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> TokenResponse:
    """Rotate access token."""
    return await auth_service.refresh_access_token(body.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Record user logout and invalidate session audit trail.",
)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> dict:
    """Logout current user."""
    client_ip = request.client.host if request.client else None
    await auth_service.logout_user(current_user.id, ip_address=client_ip)
    return {"message": "Successfully logged out"}


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Current User Profile",
    description="Fetch full authenticated user profile metadata.",
)
async def get_my_profile(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return authenticated user."""
    return UserResponse.model_validate(current_user)


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change Password",
    description="Change current user's password after verifying existing password.",
)
async def change_password(
    body: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> dict:
    """Update password."""
    await user_service.change_password(current_user.id, body)
    return {"message": "Password changed successfully"}
