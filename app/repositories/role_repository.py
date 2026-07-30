"""Role & Permission Repository Implementation."""

from typing import Optional, Sequence
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.role import Permission, Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Repository managing Role and Permission database operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Role, session=session)

    async def get_by_name(self, name: str) -> Optional[Role]:
        """Fetch role by unique name."""
        stmt = select(Role).where(Role.name == name)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all_permissions(self) -> Sequence[Permission]:
        """Fetch all system permissions."""
        stmt = select(Permission)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_permission_by_name(self, name: str) -> Optional[Permission]:
        """Fetch permission entity by name."""
        stmt = select(Permission).where(Permission.name == name)
        result = await self.session.execute(stmt)
        return result.scalars().first()
