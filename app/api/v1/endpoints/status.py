"""Server Component Status Overview Endpoint."""

from fastapi import APIRouter, status
from app.database.session import check_database_health
from app.schemas.health import StatusResponse
from app.websocket.manager import ws_manager

router = APIRouter(prefix="/status", tags=["Health & System Probes"])


@router.get(
    "",
    response_model=StatusResponse,
    status_code=status.HTTP_200_OK,
    summary="System Subsystems Status Overview",
    description="Retrieve operational status of active WebSocket connections, database connectivity, and subsystem metrics.",
)
async def get_system_status() -> StatusResponse:
    """Return runtime subsystem status snapshot."""
    db_health = await check_database_health()
    db_ok = db_health.get("status") == "healthy"

    return StatusResponse(
        status="operational" if db_ok else "degraded",
        active_websocket_connections=ws_manager.total_connections,
        database_connected=db_ok,
        system_load={"status": "normal"},
    )
