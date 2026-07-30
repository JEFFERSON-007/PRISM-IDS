"""Unit tests for UserService and UserRepository."""

from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest
from app.core.exceptions import PRISMValidationError, NotFoundError
from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_create_user_duplicate_username_raises_error() -> None:
    """Test duplicate username check in UserService."""
    user_repo = MagicMock()
    user_repo.get_by_username = AsyncMock(return_value=User(username="admin_test"))

    role_repo = MagicMock()
    audit_service = MagicMock()

    service = UserService(user_repository=user_repo, role_repository=role_repo, audit_service=audit_service)

    user_in = UserCreate(
        username="admin_test",
        email="admin@prism.io",
        password="SecurePassword123!",
        full_name="Admin Test",
        role_id=uuid.uuid4(),
    )

    with pytest.raises(PRISMValidationError):
        await service.create_user(user_in)
