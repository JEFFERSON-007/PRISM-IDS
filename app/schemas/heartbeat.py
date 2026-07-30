"""Heartbeat Submission Schemas."""

from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, Field


class HeartbeatCreate(BaseModel):
    """Heartbeat payload sent periodically by active monitoring agents."""

    timestamp: datetime = Field(description="Agent local timestamp")
    cpu_usage: float = Field(ge=0.0, le=100.0, description="CPU usage percentage")
    ram_usage: float = Field(ge=0.0, le=100.0, description="RAM usage percentage")
    disk_usage: float = Field(ge=0.0, le=100.0, description="Disk usage percentage")
    network_status: str = Field(default="ok", max_length=50)
    agent_version: str = Field(min_length=1, max_length=50)


class HeartbeatResponse(BaseModel):
    """Heartbeat record output schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_id: uuid.UUID
    timestamp: datetime
    cpu_usage: float
    ram_usage: float
    disk_usage: float
    network_status: str
    agent_version: str
    created_at: datetime
