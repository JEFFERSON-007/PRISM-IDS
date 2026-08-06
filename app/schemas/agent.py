"""Agent Registration and Management Schemas."""

from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class AgentRegisterRequest(BaseModel):
    """Payload submitted by a new monitoring agent during onboarding."""

    model_config = ConfigDict(extra="ignore")

    agent_name: str = Field(default="agent-node", min_length=1, max_length=100)
    hostname: str = Field(default="localhost", min_length=1, max_length=255)
    ip_address: Optional[str] = Field(default="127.0.0.1")
    operating_system: Optional[str] = Field(default="Windows")
    version: Optional[str] = Field(default="1.0.0")


class AgentRegisterResponse(BaseModel):
    """Registration output containing assigned UUID and generated secret key."""

    agent_id: uuid.UUID
    agent_name: str
    secret_key: str = Field(description="Unique agent secret key (stored once by agent)")
    status: str = "registered"


class AgentUpdateRequest(BaseModel):
    """Payload to update agent parameters."""

    model_config = ConfigDict(extra="ignore")

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
