"""Unit tests for Core Security, Password Hashing, JWT, and RBAC."""

import pytest
from app.authentication.jwt import create_access_token, create_refresh_token, verify_token
from app.authentication.password import hash_password, verify_password
from app.authentication.permissions import Permission, has_permission
from app.authentication.roles import Role
from app.core.exceptions import AuthenticationError


def test_password_hashing_and_verification() -> None:
    """Test password hashing and verification match."""
    plain = "MySecurePassword123!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_access_token_creation_and_verification() -> None:
    """Test JWT token generation and decoding claims."""
    token = create_access_token(
        subject="test_analyst",
        role=Role.ANALYST,
        permissions=[Permission.READ_HEALTH.value],
    )
    assert isinstance(token, str)
    payload = verify_token(token, expected_type="access")
    assert payload["sub"] == "test_analyst"
    assert payload["role"] == "analyst"
    assert Permission.READ_HEALTH.value in payload["permissions"]


def test_jwt_refresh_token_type_validation() -> None:
    """Test verification throws error when token type mismatches."""
    refresh_token = create_refresh_token(subject="test_user")
    payload = verify_token(refresh_token, expected_type="refresh")
    assert payload["sub"] == "test_user"

    with pytest.raises(AuthenticationError):
        verify_token(refresh_token, expected_type="access")


def test_rbac_permission_matrix() -> None:
    """Test role permissions mapping."""
    assert has_permission(Role.ADMIN, Permission.MANAGE_SYSTEM) is True
    assert has_permission(Role.OPERATOR, Permission.MANAGE_SYSTEM) is False
