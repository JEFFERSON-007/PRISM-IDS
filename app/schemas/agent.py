"""Agent Registration and Management Schemas."""

from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class AgentRegisterRequest(BaseModel):
    """Payload submitted by a new monitoring agent during onboarding."""

    agent_name: str = Field(min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_\-]+$")
    hostname: str = Field(min_length=1, max_length=255)
    ip_address: str = Field(min_length=7, max_length=45, description="IPv4 or IPv6 address")
    operating_system: str = Field(min_length=1, max_length=100)
    version: str = Field(min_length=1, max_length=50)


class AgentRegisterResponse(BaseModel):
    """Registration output containing assigned UUID and generated secret key."""

    agent_id: uuid.UUID
    agent_name: str
    secret_key: str = Field(description="Unique agent secret key (stored once by agent)")
    status: str = "registered"


class AgentUpdateRequest(BaseModel):
    """Payload to update agent parameters."""

    ip_address: Optional[str] = None
    version: Optional[str] = None
    health_status: Optional[str] = None


class AgentResponse(BaseModel):
    """Agent summary response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_name: str
    hostname: str
    ip_address: str
    operating_system: str
    version: str
    registration_time: datetime
    last_heartbeat: Optional[datetime] = None
    is_online: bool
    health_status: str
    created_at: datetime
    updated_at: datetime
