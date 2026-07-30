"""User Schemas with strict Pydantic v2 validation."""

from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.schemas.role import RoleResponse


class UserCreate(BaseModel):
    """User creation request schema."""

    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_\-]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128, description="Strong password min 8 characters")
    full_name: str = Field(min_length=1, max_length=100)
    role_id: uuid.UUID


class UserUpdate(BaseModel):
    """User profile update request schema."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    role_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None


class PasswordChangeRequest(BaseModel):
    """Password change request schema."""

    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    """User response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: str
    full_name: str
    is_active: bool
    role: Optional[RoleResponse] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
