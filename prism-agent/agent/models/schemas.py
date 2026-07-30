"""Pydantic v2 Schemas for Agent Communication."""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class AgentRegisterPayload(BaseModel):
    """Payload sent during agent onboarding."""

    agent_name: str
    hostname: str
    ip_address: str
    operating_system: str
    version: str


class AgentRegisterResponse(BaseModel):
    """Server registration response payload."""

    agent_id: str
    agent_name: str
    secret_key: str
    status: str


class HeartbeatPayload(BaseModel):
    """Periodic telemetry payload sent by agent."""

    timestamp: str
    cpu_usage: float = Field(ge=0.0, le=100.0)
    ram_usage: float = Field(ge=0.0, le=100.0)
    disk_usage: float = Field(ge=0.0, le=100.0)
    network_status: str = "ok"
    agent_version: str


class AgentHealthStatus(BaseModel):
    """Local agent health probe response schema."""

    status: str
    registered: bool
    authenticated: bool
    server_reachable: bool
    websocket_connected: bool
    agent_id: Optional[str] = None
    heartbeats_sent: int
    failed_heartbeats: int
    last_heartbeat: Optional[str] = None
