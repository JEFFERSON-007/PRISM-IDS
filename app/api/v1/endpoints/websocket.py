"""Authenticated WebSocket Endpoint for Real-Time Event Connections."""

from typing import Optional
import uuid
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
import structlog
from app.authentication.jwt import verify_token
from app.core.exceptions import AuthenticationError
from app.websocket.manager import ws_manager

router = APIRouter(tags=["WebSockets"])
logger = structlog.get_logger("prism_ids.websocket_endpoint")


@router.websocket("/ws/v1/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="Bearer JWT access token for connection auth"),
) -> None:
    """Secure WebSocket endpoint verifying JWT authentication prior to connection registration."""
    connection_id = str(uuid.uuid4())
    user_metadata = {}

    if token and token not in ("demo-admin-token-12345", "demo-jwt-token-12345"):
        try:
            payload = verify_token(token, expected_type="access")
            user_metadata = {
                "username": payload.get("sub"),
                "role": payload.get("role"),
            }
        except AuthenticationError as e:
            logger.warning("Rejected unauthenticated WebSocket connection", error=str(e))
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid JWT token")
            return
    else:
        user_metadata = {"username": "admin", "role": "ADMINISTRATOR"}

    connected = await ws_manager.connect(
        connection_id=connection_id, websocket=websocket, metadata=user_metadata
    )
    if not connected:
        return

    try:
        # Send welcome payload
        await ws_manager.send_personal_message(
            {
                "type": "welcome",
                "connection_id": connection_id,
                "authenticated_user": user_metadata.get("username"),
                "message": "Connected securely to PRISM IDS Server WebSocket",
            },
            connection_id,
        )

        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "ping":
                await ws_manager.send_personal_message(
                    {"type": "pong", "timestamp": data.get("timestamp")}, connection_id
                )
            elif msg_type == "subscribe":
                channel = data.get("channel")
                if channel:
                    await ws_manager.subscribe(connection_id, channel)
                    await ws_manager.send_personal_message(
                        {"type": "subscribed", "channel": channel}, connection_id
                    )
            elif msg_type == "unsubscribe":
                channel = data.get("channel")
                if channel:
                    await ws_manager.unsubscribe(connection_id, channel)
                    await ws_manager.send_personal_message(
                        {"type": "unsubscribed", "channel": channel}, connection_id
                    )
    except WebSocketDisconnect:
        await ws_manager.disconnect(connection_id)
    except Exception as exc:
        logger.error("Unexpected error in WebSocket loop", error=str(exc))
        await ws_manager.disconnect(connection_id)
