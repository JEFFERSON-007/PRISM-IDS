"""Dashboard Metrics REST API Endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    NetworkAnalyticsResponse,
    SystemHealthResponse,
)
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
logger = structlog.get_logger("prism_ids.dashboard_api")


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardSummaryResponse:
    """Fetch executive SOC summary metrics (Requires JWT Auth)."""
    service = DashboardService(db)
    return await service.get_dashboard_summary()


@router.get("/network", response_model=NetworkAnalyticsResponse)
async def get_network_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NetworkAnalyticsResponse:
    """Fetch network traffic analytics & protocol distributions (Requires JWT Auth)."""
    service = DashboardService(db)
    return await service.get_network_analytics()


@router.get("/system", response_model=SystemHealthResponse)
async def get_system_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SystemHealthResponse:
    """Fetch server, database, agent, and WebSocket system health (Requires JWT Auth)."""
    service = DashboardService(db)
    return await service.get_system_health()
