"""Agent Heartbeat Processing and Health Monitoring Service."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence
import uuid
import structlog
from app.models.heartbeat import Heartbeat
from app.repositories.agent_repository import AgentRepository
from app.repositories.heartbeat_repository import HeartbeatRepository
from app.schemas.heartbeat import HeartbeatCreate
from app.services.audit_service import AuditService

logger = structlog.get_logger("prism_ids.heartbeat_service")

# Configurable threshold: agents missing heartbeats for > 90 seconds are marked offline/unhealthy
HEARTBEAT_TIMEOUT_SECONDS = 90


class HeartbeatService:
    """Service handling agent periodic health telemetry and timeout detection."""

    def __init__(
        self,
        heartbeat_repository: HeartbeatRepository,
        agent_repository: AgentRepository,
        audit_service: AuditService,
    ) -> None:
        self.heartbeat_repo = heartbeat_repository
        self.agent_repo = agent_repository
        self.audit_service = audit_service

    async def record_heartbeat(
        self, agent_id: uuid.UUID, data: HeartbeatCreate
    ) -> Heartbeat:
        """Process incoming agent heartbeat telemetry and evaluate agent health."""
        # Calculate health status based on metrics
        health_status = "healthy"
        if data.cpu_usage > 90.0 or data.ram_usage > 90.0 or data.disk_usage > 95.0:
            health_status = "degraded"
        if data.network_status != "ok":
            health_status = "unhealthy"

        heartbeat = Heartbeat(
            agent_id=agent_id,
            timestamp=data.timestamp,
            cpu_usage=data.cpu_usage,
            ram_usage=data.ram_usage,
            disk_usage=data.disk_usage,
            network_status=data.network_status,
            agent_version=data.agent_version,
        )
        saved_hb = await self.heartbeat_repo.create(heartbeat)

        # Update Agent master table state
        now = datetime.now(timezone.utc)
        await self.agent_repo.update_heartbeat_status(
            agent_id=agent_id,
            timestamp=now,
            health_status=health_status,
        )

        logger.debug("Recorded heartbeat for agent", agent_id=str(agent_id), health_status=health_status)
        return saved_hb

    async def detect_and_mark_offline_agents(self) -> int:
        """Scan and update agents that have missed heartbeat threshold to offline/unhealthy."""
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=HEARTBEAT_TIMEOUT_SECONDS)
        offline_count = await self.agent_repo.mark_offline_inactive_agents(cutoff)
        if offline_count > 0:
            logger.info("Marked stale agents offline", count=offline_count)
        return offline_count

    async def get_agent_heartbeat_history(
        self, agent_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Sequence[Heartbeat]:
        """Fetch historical heartbeat telemetry for an agent."""
        return await self.heartbeat_repo.get_history_by_agent_id(agent_id, skip=skip, limit=limit)
