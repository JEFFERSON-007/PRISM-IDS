"""Agent Configuration Schemas."""

from datetime import datetime
from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class AgentConfigUpdate(BaseModel):
    """Payload to modify agent configuration parameters."""

    capture_interface: Optional[str] = Field(default=None, max_length=50)
    packet_filters: Optional[str] = Field(default=None, max_length=255)
    log_level: Optional[str] = Field(default=None, max_length=20)
    sampling_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    custom_config: Optional[Dict[str, Any]] = None


class AgentConfigResponse(BaseModel):
    """Agent configuration output schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_id: uuid.UUID
    version: int
    capture_interface: str
    packet_filters: str
    log_level: str
    sampling_rate: float
    custom_config: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
