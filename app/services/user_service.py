"""User Management Service."""

from typing import Optional, Sequence
import uuid
from app.authentication.password import hash_password, verify_password
from app.core.exceptions import AuthenticationError, PRISMValidationError, NotFoundError
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import PasswordChangeRequest, UserCreate, UserUpdate
from app.services.audit_service import AuditService


class UserService:
    """Service handling user account lifecycle, profiles, and password updates."""

    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        audit_service: AuditService,
    ) -> None:
        self.user_repo = user_repository
        self.role_repo = role_repository
        self.audit_service = audit_service

    async def create_user(self, user_in: UserCreate, creator_id: Optional[uuid.UUID] = None) -> User:
        """Create a new user account with role validation."""
        # Check duplicate username or email
        existing_username = await self.user_repo.get_by_username(user_in.username)
        if existing_username:
            raise PRISMValidationError(f"Username '{user_in.username}' is already registered")

        existing_email = await self.user_repo.get_by_email(user_in.email)
        if existing_email:
            raise PRISMValidationError(f"Email '{user_in.email}' is already registered")

        # Validate role exists
        role = await self.role_repo.get_by_id(user_in.role_id)
        if not role:
            raise NotFoundError(f"Role with ID '{user_in.role_id}' does not exist")

        hashed_pwd = hash_password(user_in.password)
        new_user = User(
            username=user_in.username,
            email=user_in.email,
            password_hash=hashed_pwd,
            full_name=user_in.full_name,
            role_id=user_in.role_id,
            is_active=True,
        )
        saved_user = await self.user_repo.create(new_user)

        await self.audit_service.log_event(
            user_id=creator_id,
            action="CREATE_USER",
            resource=f"user:{saved_user.id}",
            details={"username": saved_user.username, "role": role.name},
        )
        return saved_user

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        """Fetch user by ID."""
        user = await self.user_repo.get_by_id(user_id)
        if not user or user.deleted_at is not None:
            raise NotFoundError(f"User with ID '{user_id}' not found")
        return user

    async def get_users(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """Fetch active users."""
        return await self.user_repo.get_all(skip=skip, limit=limit)

    async def update_user(
        self, user_id: uuid.UUID, obj_in: UserUpdate, modifier_id: Optional[uuid.UUID] = None
    ) -> User:
        """Update user parameters."""
        user = await self.get_user_by_id(user_id)
        update_data = obj_in.model_dump(exclude_unset=True)

        if "role_id" in update_data and update_data["role_id"]:
            role = await self.role_repo.get_by_id(update_data["role_id"])
            if not role:
                raise NotFoundError(f"Role with ID '{update_data['role_id']}' not found")

        for field, value in update_data.items():
            setattr(user, field, value)

        updated_user = await self.user_repo.update(user)
        await self.audit_service.log_event(
            user_id=modifier_id,
            action="UPDATE_USER",
            resource=f"user:{user.id}",
            details=update_data,
        )
        return updated_user

    async def change_password(
        self, user_id: uuid.UUID, body: PasswordChangeRequest
    ) -> None:
        """Change user password after verifying current password."""
        user = await self.get_user_by_id(user_id)
        if not verify_password(body.current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect")

        user.password_hash = hash_password(body.new_password)
        await self.user_repo.update(user)

        await self.audit_service.log_event(
            user_id=user_id,
            action="CHANGE_PASSWORD",
            resource=f"user:{user_id}",
        )

    async def disable_user(self, user_id: uuid.UUID, modifier_id: Optional[uuid.UUID] = None) -> User:
        """Disable user account."""
        user = await self.get_user_by_id(user_id)
        user.is_active = False
        updated = await self.user_repo.update(user)
        await self.audit_service.log_event(
            user_id=modifier_id,
            action="DISABLE_USER",
            resource=f"user:{user_id}",
        )
        return updated
