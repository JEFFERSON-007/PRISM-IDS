"""JWT Infrastructure for Access and Refresh Token Generation & Validation."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import jwt
from app.authentication.roles import Role
from app.core.config import settings
from app.core.exceptions import AuthenticationError


def create_access_token(
    subject: str,
    role: Role = Role.ANALYST,
    permissions: Optional[List[str]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generate a signed JWT Access Token containing subject, role, permissions, and expiration."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "sub": subject,
        "role": role.value if isinstance(role, Role) else role,
        "permissions": permissions or [],
        "type": "access",
        "iat": now,
        "exp": expire,
        "iss": settings.APP_NAME,
    }
    encoded_jwt = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generate a signed JWT Refresh Token with extended expiration."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload: Dict[str, Any] = {
        "sub": subject,
        "type": "refresh",
        "iat": now,
        "exp": expire,
        "iss": settings.APP_NAME,
    }
    encoded_jwt = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str, expected_type: str = "access") -> Dict[str, Any]:
    """Verify signature, expiration, and token type claim."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        token_type = payload.get("type")
        if token_type != expected_type:
            raise AuthenticationError(f"Invalid token type: expected '{expected_type}', got '{token_type}'")
        return payload
    except jwt.ExpiredSignatureError as e:
        raise AuthenticationError("JWT token has expired") from e
    except jwt.PyJWTError as e:
        raise AuthenticationError(f"Invalid JWT token signature or format: {str(e)}") from e
