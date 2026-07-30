"""Alert Ingestion and Query REST API Endpoints."""

from datetime import datetime
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from app.api.dependencies import get_authenticated_agent, get_current_user, get_db
from app.models.agent import Agent
from app.models.user import User
from app.schemas.alert import AlertCreate, AlertPaginationResponse, AlertRead
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])
logger = structlog.get_logger("prism_ids.alerts_api")


@router.post("", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
async def ingest_alert(
    alert_in: AlertCreate,
    x_agent_id: Optional[str] = Header(None, alias="X-Agent-ID"),
    db: AsyncSession = Depends(get_db),
    agent: Optional[Agent] = Depends(get_authenticated_agent),
) -> AlertRead:
    """Ingest security alert from PRISM IDS Agent node."""
    service = AlertService(db)
    agent_id_str = agent.agent_id if agent else x_agent_id
    alert_read = await service.ingest_alert(alert_in, header_agent_id=agent_id_str)
    return alert_read


@router.get("", response_model=AlertPaginationResponse)
async def list_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: OPEN, ACKNOWLEDGED, RESOLVED"),
    protocol: Optional[str] = Query(None, description="Filter by transport protocol: TCP, UDP, ICMP"),
    detection_method: Optional[str] = Query(None, description="Filter by method: SIGNATURE, MACHINE_LEARNING, HYBRID"),
    src_ip: Optional[str] = Query(None, description="Filter by source IP address"),
    dst_ip: Optional[str] = Query(None, description="Filter by destination IP address"),
    agent_id: Optional[uuid.UUID] = Query(None, description="Filter by agent UUID"),
    start_time: Optional[datetime] = Query(None, description="Filter by start UTC datetime"),
    end_time: Optional[datetime] = Query(None, description="Filter by end UTC datetime"),
    search: Optional[str] = Query(None, description="Full text search across IP, rule name, protocol, alert ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertPaginationResponse:
    """Query, filter, and paginate security alerts (Requires JWT Auth)."""
    service = AlertService(db)
    return await service.get_alerts_paginated(
        severity=severity,
        status=status_filter,
        protocol=protocol,
        detection_method=detection_method,
        src_ip=src_ip,
        dst_ip=dst_ip,
        agent_id=agent_id,
        start_time=start_time,
        end_time=end_time,
        search_query=search,
        page=page,
        page_size=page_size,
    )


@router.get("/{alert_id}", response_model=AlertRead)
async def get_alert_details(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertRead:
    """Fetch detailed alert by alert_id string or UUID (Requires JWT Auth)."""
    service = AlertService(db)
    alert = await service.get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert
