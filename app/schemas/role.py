"""Role and Permission Schemas."""

from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict


class PermissionResponse(BaseModel):
    """Permission response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    category: str


class RoleResponse(BaseModel):
    """Role response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    permissions: List[PermissionResponse] = []
