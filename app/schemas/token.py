"""JWT Token Request and Response Schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.authentication.roles import Role


class Token(BaseModel):
    """JWT Token Pair Response."""

    access_token: str = Field(description="JWT Access Token")
    refresh_token: str = Field(description="JWT Refresh Token")
    token_type: str = Field(default="bearer", description="Token Authorization Type")
    expires_in: int = Field(description="Access token lifespan in seconds")


class TokenData(BaseModel):
    """Decoded Access Token Subject Data."""

    username: Optional[str] = None
    role: Optional[Role] = None
    permissions: List[str] = Field(default_factory=list)


class TokenPayload(BaseModel):
    """JWT Decoded Claims Payload."""

    sub: str
    role: str
    permissions: List[str] = Field(default_factory=list)
    type: str
    iat: int
    exp: int
    iss: str
