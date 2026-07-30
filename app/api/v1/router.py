"""Main API Version 1 Router Aggregator."""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    agents,
    alerts,
    audit,
    auth,
    dashboard,
    health,
    incidents,
    llm,
    mitre,
    monitoring,
    reports,
    roles,
    status,
    users,
)

api_v1_router = APIRouter()

api_v1_router.include_router(health.router)
api_v1_router.include_router(status.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(users.router)
api_v1_router.include_router(roles.router)
api_v1_router.include_router(agents.router)
api_v1_router.include_router(audit.router)
api_v1_router.include_router(alerts.router)
api_v1_router.include_router(incidents.router)
api_v1_router.include_router(dashboard.router)
api_v1_router.include_router(llm.router)
api_v1_router.include_router(mitre.router)
api_v1_router.include_router(reports.router)
api_v1_router.include_router(monitoring.router)
