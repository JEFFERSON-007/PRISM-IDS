"""User Repository Implementation."""

from datetime import datetime, timezone
from typing import Optional, Sequence
import uuid
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository handling database access for User entity."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=User, session=session)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Find non-deleted user by username."""
        stmt = select(User).where(User.username == username, User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Find non-deleted user by email address."""
        stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """Fetch active non-deleted users."""
        stmt = select(User).where(User.is_active.is_(True), User.deleted_at.is_(None)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_last_login(self, user_id: uuid.UUID) -> None:
        """Update user's last login timestamp and reset failed login attempts."""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(
                last_login=datetime.now(timezone.utc),
                failed_login_attempts=0,
                locked_until=None,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def increment_failed_attempts(self, user_id: uuid.UUID, lock_until: Optional[datetime] = None) -> int:
        """Increment failed login counter and set locked_until timestamp if threshold reached."""
        user = await self.get_by_id(user_id)
        if not user:
            return 0
        attempts = user.failed_login_attempts + 1
        user.failed_login_attempts = attempts
        if lock_until:
            user.locked_until = lock_until
        await self.update(user)
        return attempts

    async def soft_delete(self, user_id: uuid.UUID) -> bool:
        """Soft delete user by setting deleted_at timestamp and disabling account."""
        user = await self.get_by_id(user_id)
        if user:
            user.deleted_at = datetime.now(timezone.utc)
            user.is_active = False
            await self.update(user)
            return True
        return False
