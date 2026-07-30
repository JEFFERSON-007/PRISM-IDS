"""System Health, Readiness, and Liveness Probe Endpoints."""

import time
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.core.config import Settings
from app.api.dependencies import get_settings
from app.database.session import check_database_health
from app.schemas.health import HealthCheckResponse, LivenessResponse, ReadinessResponse
from app.utils.datetime import utc_now, format_iso

router = APIRouter(prefix="/health", tags=["Health & System Probes"])
start_timestamp = time.time()


@router.get(
    "",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete System Health Diagnostics",
    description="Check server state, version info, database connection health, and latency.",
)
async def get_health(settings: Settings = Depends(get_settings)) -> HealthCheckResponse:
    """Return comprehensive health diagnostics."""
    db_health = await check_database_health()
    return HealthCheckResponse(
        status="healthy" if db_health.get("status") == "healthy" else "degraded",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=format_iso(utc_now()),
        database=db_health,
    )


@router.get(
    "/readiness",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Kubernetes Readiness Probe",
    description="Probe endpoint returning 200 OK if database and server dependencies are ready to serve traffic.",
)
async def get_readiness() -> ReadinessResponse | JSONResponse:
    """Return readiness state for load balancer routing."""
    db_health = await check_database_health()
    is_db_ok = db_health.get("status") == "healthy"
    ready = is_db_ok

    payload = ReadinessResponse(
        ready=ready,
        checks={
            "database": "ok" if is_db_ok else "failed",
            "websocket_manager": "ok",
        },
    )

    if not ready:
        return JSONResponse(
            status_code=status.HTTP_530_SERVICE_ERROR if hasattr(status, "HTTP_530_SERVICE_ERROR") else 503,
            content=payload.model_dump(),
        )

    return payload


@router.get(
    "/liveness",
    response_model=LivenessResponse,
    status_code=status.HTTP_200_OK,
    summary="Kubernetes Liveness Probe",
    description="Simple probe checking if the process container is alive.",
)
async def get_liveness() -> LivenessResponse:
    """Return liveness probe status."""
    uptime = time.time() - start_timestamp
    return LivenessResponse(alive=True, uptime_seconds=round(uptime, 2))
