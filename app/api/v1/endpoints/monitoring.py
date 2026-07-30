"""System Monitoring, Prometheus Metrics, and Health Probes."""

from datetime import datetime, timezone
import psutil
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from app.database.session import check_database_health, get_db

router = APIRouter(prefix="/monitoring", tags=["System Monitoring & Observability"])
logger = structlog.get_logger("prism_ids.monitoring_api")


@router.get("/liveness", response_model=dict)
async def liveness_probe() -> dict:
    """Kubernetes / Docker Liveness probe."""
    return {"status": "UP", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/readiness", response_model=dict)
async def readiness_probe(db: AsyncSession = Depends(get_db)) -> dict:
    """Kubernetes / Docker Readiness probe checking DB connection status."""
    db_status = await check_database_health()
    is_ready = db_status.get("status") == "healthy"
    return {
        "status": "READY" if is_ready else "NOT_READY",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/metrics")
async def get_metrics() -> Response:
    """Prometheus-formatted System & Application Metrics endpoint."""
    cpu_pct = psutil.cpu_percent()
    mem_pct = psutil.virtual_memory().percent

    prometheus_metrics = f"""# HELP prism_cpu_usage_percent Current CPU utilization percentage
# TYPE prism_cpu_usage_percent gauge
prism_cpu_usage_percent {cpu_pct}

# HELP prism_memory_usage_percent Current Virtual Memory utilization percentage
# TYPE prism_memory_usage_percent gauge
prism_memory_usage_percent {mem_pct}

# HELP prism_up Application uptime indicator
# TYPE prism_up gauge
prism_up 1.0
"""
    return Response(content=prometheus_metrics, media_type="text/plain")
