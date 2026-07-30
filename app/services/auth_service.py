"""Authentication Service handling user login, lockout, and JWT token rotation."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import uuid
import structlog
from app.authentication.jwt import create_access_token, create_refresh_token, verify_token
from app.authentication.password import verify_password
from app.authentication.roles import Role as RoleEnum
from app.core.config import settings
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.audit_service import AuditService

logger = structlog.get_logger("prism_ids.auth_service")

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


class AuthenticationService:
    """Service executing security authentication pipelines."""

    def __init__(self, user_repository: UserRepository, audit_service: AuditService) -> None:
        self.user_repo = user_repository
        self.audit_service = audit_service

    async def authenticate_user(self, credentials: LoginRequest, ip_address: Optional[str] = None) -> TokenResponse:
        """Authenticate user credentials and enforce account lockout policies."""
        # Find user by username or email
        user = await self.user_repo.get_by_username(credentials.username)
        if not user:
            user = await self.user_repo.get_by_email(credentials.username)

        if not user:
            await self.audit_service.log_event(
                action="LOGIN_FAILED",
                resource="auth",
                ip_address=ip_address,
                details={"username": credentials.username, "reason": "User not found"},
                status="failure",
            )
            raise AuthenticationError("Invalid username or password")

        # Check soft deletion & active state
        if user.deleted_at is not None or not user.is_active:
            await self.audit_service.log_event(
                user_id=user.id,
                action="LOGIN_FAILED",
                resource="auth",
                ip_address=ip_address,
                details={"reason": "Account disabled or deleted"},
                status="failure",
            )
            raise PermissionDeniedError("Account is inactive or disabled")

        # Check account lockout status
        now = datetime.now(timezone.utc)
        if user.locked_until and user.locked_until > now:
            minutes_left = round((user.locked_until - now).total_seconds() / 60, 1)
            await self.audit_service.log_event(
                user_id=user.id,
                action="LOGIN_FAILED",
                resource="auth",
                ip_address=ip_address,
                details={"reason": "Account locked", "minutes_remaining": minutes_left},
                status="failure",
            )
            raise AuthenticationError(f"Account locked due to failed logins. Try again in {minutes_left} minutes.")

        # Verify password hash
        if not verify_password(credentials.password, user.password_hash):
            lock_until = None
            attempts = user.failed_login_attempts + 1
            if attempts >= MAX_FAILED_ATTEMPTS:
                lock_until = now + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                logger.warning("Account locked due to consecutive failed logins", user_id=str(user.id))

            await self.user_repo.increment_failed_attempts(user.id, lock_until=lock_until)
            await self.audit_service.log_event(
                user_id=user.id,
                action="LOGIN_FAILED",
                resource="auth",
                ip_address=ip_address,
                details={"failed_attempts": attempts},
                status="failure",
            )
            raise AuthenticationError("Invalid username or password")

        # Login successful -> update last login and reset failed attempts
        await self.user_repo.update_last_login(user.id)

        # Issue JWT Access & Refresh Token Pair
        role_name = user.role.name if user.role else "analyst"
        permissions_list = [p.name for p in user.role.permissions] if user.role and user.role.permissions else []

        try:
            role_enum = RoleEnum(role_name.lower())
        except ValueError:
            role_enum = RoleEnum.ANALYST

        access_token = create_access_token(
            subject=user.username,
            role=role_enum,
            permissions=permissions_list,
        )
        refresh_token = create_refresh_token(subject=user.username)

        await self.audit_service.log_event(
            user_id=user.id,
            action="LOGIN_SUCCESS",
            resource="auth",
            ip_address=ip_address,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Validate refresh token and issue new token pair."""
        payload = verify_token(refresh_token, expected_type="refresh")
        username = payload.get("sub")
        if not username:
            raise AuthenticationError("Invalid token subject payload")

        user = await self.user_repo.get_by_username(username)
        if not user or not user.is_active:
            raise AuthenticationError("User associated with refresh token is no longer active")

        role_name = user.role.name if user.role else "analyst"
        permissions_list = [p.name for p in user.role.permissions] if user.role and user.role.permissions else []

        try:
            role_enum = RoleEnum(role_name.lower())
        except ValueError:
            role_enum = RoleEnum.ANALYST

        new_access_token = create_access_token(
            subject=user.username,
            role=role_enum,
            permissions=permissions_list,
        )
        new_refresh_token = create_refresh_token(subject=user.username)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )

    async def logout_user(self, user_id: uuid.UUID, ip_address: Optional[str] = None) -> None:
        """Record logout audit event."""
        await self.audit_service.log_event(
            user_id=user_id,
            action="LOGOUT",
            resource="auth",
            ip_address=ip_address,
        )
