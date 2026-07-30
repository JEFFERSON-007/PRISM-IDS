"""Audit Logging Service."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Sequence
import uuid
import structlog
from app.models.audit_log import AuditLog
from app.repositories.audit_repository import AuditRepository

logger = structlog.get_logger("prism_ids.audit_service")


class AuditService:
    """Service recording and querying security audit events."""

    def __init__(self, audit_repository: AuditRepository) -> None:
        self.audit_repo = audit_repository

    async def log_event(
        self,
        action: str,
        resource: str,
        user_id: Optional[uuid.UUID] = None,
        agent_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
    ) -> AuditLog:
        """Create and persist a new security audit log record."""
        audit_entry = AuditLog(
            user_id=user_id,
            agent_id=agent_id,
            action=action,
            resource=resource,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
            status=status,
            timestamp=datetime.now(timezone.utc),
        )
        saved = await self.audit_repo.create(audit_entry)
        logger.info(
            "Audit log event recorded",
            action=action,
            resource=resource,
            user_id=str(user_id) if user_id else None,
            agent_id=str(agent_id) if agent_id else None,
            status=status,
        )
        return saved

    async def get_logs(
        self,
        user_id: Optional[uuid.UUID] = None,
        agent_id: Optional[uuid.UUID] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[AuditLog]:
        """Fetch audit log records."""
        return await self.audit_repo.search_logs(
            user_id=user_id,
            agent_id=agent_id,
            action=action,
            resource=resource,
            skip=skip,
            limit=limit,
        )
