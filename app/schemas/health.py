"""Health, Readiness, and System Status Schemas."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Detailed health check output schema."""

    status: str = Field(example="healthy")
    app_name: str = Field(example="PRISM IDS Server")
    version: str = Field(example="1.0.0")
    environment: str = Field(example="development")
    timestamp: str = Field(example="2026-07-30T15:30:00Z")
    database: Dict[str, Any] = Field(
        example={"status": "healthy", "latency_ms": 1.25, "pool_size": 10}
    )


class ReadinessResponse(BaseModel):
    """Kubernetes / Readiness check schema."""

    ready: bool = Field(example=True)
    checks: Dict[str, str] = Field(example={"database": "ok", "websocket": "ok"})


class LivenessResponse(BaseModel):
    """Kubernetes / Liveness check schema."""

    alive: bool = Field(example=True)
    uptime_seconds: float = Field(example=120.45)


class StatusResponse(BaseModel):
    """System overview and active subsystems status."""

    status: str = Field(example="operational")
    active_websocket_connections: int = Field(example=5)
    database_connected: bool = Field(example=True)
    system_load: Optional[Dict[str, Any]] = None
