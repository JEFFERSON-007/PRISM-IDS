"""Authentication Request and Response Schemas."""

from pydantic import BaseModel, Field
from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    """User authentication login payload."""

    username: str = Field(description="Username or registered email address")
    password: str = Field(description="User password")


class RefreshTokenRequest(BaseModel):
    """Refresh token rotation payload."""

    refresh_token: str = Field(description="Valid JWT refresh token")


class TokenResponse(BaseModel):
    """Successful authentication token pair response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
