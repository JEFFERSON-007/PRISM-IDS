"""Role & Permission Management Service."""

from typing import Optional, Sequence
import uuid
from app.core.exceptions import NotFoundError
from app.models.role import Permission, Role
from app.repositories.role_repository import RoleRepository


class RoleService:
    """Service handling RBAC roles and permissions."""

    def __init__(self, role_repository: RoleRepository) -> None:
        self.role_repo = role_repository

    async def get_all_roles((skip: int = 0, limit: int = 100)) -> Sequence[Role]:
        """Fetch all system roles."""
        return await self.role_repo.get_all(skip=skip, limit=limit)

    async def get_role_by_id(self, role_id: uuid.UUID) -> Role:
        """Fetch role by primary key."""
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundError(f"Role with ID '{role_id}' not found")
        return role

    async def get_role_by_name(self, name: str) -> Role:
        """Fetch role by name."""
        role = await self.role_repo.get_by_name(name)
        if not role:
            raise NotFoundError(f"Role '{name}' not found")
        return role

    async def get_all_permissions(self) -> Sequence[Permission]:
        """Fetch all fine-grained permissions."""
        return await self.role_repo.get_all_permissions()
