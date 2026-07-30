"""Core Security Utilities for Password Hashing and Cryptographic Token Verification."""

from datetime import datetime, timezone
import jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.core.exceptions import AuthenticationError

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash plain text password using secure hashing algorithm."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain text password against hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def decode_jwt_token(token: str) -> dict:
    """Decode and validate JWT token signature and expiration."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        exp = payload.get("exp")
        if exp is not None:
            now = datetime.now(timezone.utc).timestamp()
            if now > exp:
                raise AuthenticationError("JWT token has expired")
        return payload
    except jwt.PyJWTError as e:
        raise AuthenticationError(f"Invalid JWT token: {str(e)}") from e
