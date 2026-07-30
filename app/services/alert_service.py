"""Alert Ingestion and Management Service."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from app.models.alert import Alert
from app.repositories.agent_repository import AgentRepository
from app.repositories.alert_repository import AlertRepository
from app.schemas.alert import AlertCreate, AlertPaginationResponse, AlertRead
from app.websocket.manager import ws_manager

logger = structlog.get_logger("prism_ids.alert_service")


class AlertService:
    """Service handling alert ingestion, querying, and real-time WebSocket broadcasting."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.alert_repo = AlertRepository(session)
        self.agent_repo = AgentRepository(session)

    async def ingest_alert(self, alert_in: AlertCreate, header_agent_id: Optional[str] = None) -> AlertRead:
        """Process and store incoming security alert from an agent node, broadcasting over WebSockets."""
        # Resolve agent ORM record if header_agent_id or schema agent_id provided
        agent_db_id: Optional[uuid.UUID] = None
        target_agent_str = header_agent_id or alert_in.agent_id

        if target_agent_str:
            try:
                agent = await self.agent_repo.get_by_agent_id(target_agent_str)
                if agent:
                    agent_db_id = agent.id
            except Exception as exc:
                logger.warning("Could not resolve agent_id for alert", agent_id=target_agent_str, error=str(exc))

        # Check if alert already exists (deduplication on server)
        existing_alert = await self.alert_repo.get_by_alert_id(alert_in.alert_id)
        if existing_alert:
            existing_alert.occurrence_count = alert_in.occurrence_count
            existing_alert.last_seen = alert_in.last_seen or alert_in.timestamp
            existing_alert.risk_score = alert_in.risk_score
            existing_alert.severity = alert_in.severity
            await self.session.commit()
            await self.session.refresh(existing_alert)
            logger.info("Updated existing alert record", alert_id=alert_in.alert_id, count=existing_alert.occurrence_count)
            alert_orm = existing_alert
        else:
            # Create new Alert ORM
            alert_orm = Alert(
                alert_id=alert_in.alert_id,
                timestamp=alert_in.timestamp,
                first_seen=alert_in.first_seen or alert_in.timestamp,
                last_seen=alert_in.last_seen or alert_in.timestamp,
                detection_id=alert_in.detection_id,
                agent_id=agent_db_id,
                flow_id=alert_in.flow_id,
                src_ip=alert_in.src_ip,
                dst_ip=alert_in.dst_ip,
                src_port=alert_in.src_port,
                dst_port=alert_in.dst_port,
                protocol=alert_in.protocol,
                risk_score=alert_in.risk_score,
                severity=alert_in.severity.upper(),
                detection_method=alert_in.detection_method.upper(),
                matched_rules=alert_in.matched_rules,
                ml_prediction=alert_in.ml_prediction,
                confidence=alert_in.confidence,
                evidence_summary=alert_in.evidence_summary,
                status=alert_in.status.upper(),
                occurrence_count=alert_in.occurrence_count,
                correlation_id=alert_in.correlation_id,
            )
            await self.alert_repo.create(alert_orm)
            await self.session.commit()
            await self.session.refresh(alert_orm)
            logger.info("Ingested new alert record", alert_id=alert_orm.alert_id, severity=alert_orm.severity)

        # Broadcast live alert event to connected WebSocket subscribers
        alert_payload = AlertRead.model_validate(alert_orm).model_dump(mode="json")
        await ws_manager.broadcast(
            {
                "type": "NEW_ALERT",
                "alert": alert_payload,
            },
            channel="alerts",
        )
        # Also broadcast globally to general subscribers
        await ws_manager.broadcast(
            {
                "type": "NEW_ALERT",
                "alert": alert_payload,
            }
        )

        return AlertRead.model_validate(alert_orm)

    async def get_alerts_paginated(
        self,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        protocol: Optional[str] = None,
        detection_method: Optional[str] = None,
        src_ip: Optional[str] = None,
        dst_ip: Optional[str] = None,
        agent_id: Optional[uuid.UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        search_query: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> AlertPaginationResponse:
        """Query and filter alerts with pagination."""
        items, total_records, total_pages = await self.alert_repo.filter_alerts(
            severity=severity,
            status=status,
            protocol=protocol,
            detection_method=detection_method,
            src_ip=src_ip,
            dst_ip=dst_ip,
            agent_id=agent_id,
            start_time=start_time,
            end_time=end_time,
            search_query=search_query,
            page=page,
            page_size=page_size,
        )

        read_items = [AlertRead.model_validate(item) for item in items]
        return AlertPaginationResponse(
            items=read_items,
            page=page,
            page_size=page_size,
            total_records=total_records,
            total_pages=total_pages,
        )

    async def get_alert_by_id(self, alert_id_or_uuid: str) -> Optional[AlertRead]:
        """Fetch alert by string alert_id or UUID string."""
        alert = await self.alert_repo.get_by_alert_id(alert_id_or_uuid)
        if not alert:
            try:
                u_id = uuid.UUID(alert_id_or_uuid)
                alert = await self.alert_repo.get_by_id(u_id)
            except ValueError:
                pass

        if not alert:
            return None
        return AlertRead.model_validate(alert)
