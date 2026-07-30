"""Audit Log Schemas."""

from datetime import datetime
from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    """Audit log entry response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    agent_id: Optional[uuid.UUID] = None
    action: str
    resource: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    status: str
    timestamp: datetime
