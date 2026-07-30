"""WebSocket Connection Manager for Real-Time Event Dispatching."""

import asyncio
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, status
import structlog
from app.core.config import settings

logger = structlog.get_logger("prism_ids.websocket")


class ConnectionManager:
    """Manages active WebSocket client connections, channels, heartbeat, and broadcasting."""

    def __init__(self) -> None:
        # Client websocket mapping by connection_id
        self.active_connections: Dict[str, WebSocket] = {}
        # Channel subscriptions: channel_name -> set of connection_ids
        self.channel_subscriptions: Dict[str, Set[str]] = {}
        # Metadata storage for authenticated users/roles per connection
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    @property
    def total_connections(self) -> int:
        """Return total active WebSocket connections."""
        return len(self.active_connections)

    async def connect(
        self,
        connection_id: str,
        websocket: WebSocket,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Accept connection and register client if max limit not exceeded."""
        if self.total_connections >= settings.WS_MAX_CONNECTIONS:
            logger.warning("Max WebSocket connections reached, rejecting connection", connection_id=connection_id)
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Max connections exceeded")
            return False

        await websocket.accept()
        async with self._lock:
            self.active_connections[connection_id] = websocket
            self.connection_metadata[connection_id] = metadata or {}

        logger.info(
            "WebSocket client connected",
            connection_id=connection_id,
            total_active=self.total_connections,
        )
        return True

    async def disconnect(self, connection_id: str) -> None:
        """Unregister client and clean up channel subscriptions."""
        async with self._lock:
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]

            if connection_id in self.connection_metadata:
                del self.connection_metadata[connection_id]

            # Remove from channels
            for channel, subscribers in list(self.channel_subscriptions.items()):
                subscribers.discard(connection_id)
                if not subscribers:
                    del self.channel_subscriptions[channel]

        logger.info(
            "WebSocket client disconnected",
            connection_id=connection_id,
            total_active=self.total_connections,
        )

    async def send_personal_message(self, message: Dict[str, Any], connection_id: str) -> bool:
        """Send JSON message directly to a specific connected client."""
        websocket = self.active_connections.get(connection_id)
        if websocket:
            try:
                await websocket.send_json(message)
                return True
            except Exception as exc:
                logger.error("Failed to send message to client", connection_id=connection_id, error=str(exc))
                await self.disconnect(connection_id)
        return False

    async def subscribe(self, connection_id: str, channel: str) -> None:
        """Subscribe client connection to a named topic/channel."""
        async with self._lock:
            if channel not in self.channel_subscriptions:
                self.channel_subscriptions[channel] = set()
            self.channel_subscriptions[channel].add(connection_id)
        logger.debug("Client subscribed to channel", connection_id=connection_id, channel=channel)

    async def unsubscribe(self, connection_id: str, channel: str) -> None:
        """Unsubscribe client connection from a named topic/channel."""
        async with self._lock:
            if channel in self.channel_subscriptions:
                self.channel_subscriptions[channel].discard(connection_id)

    async def broadcast(self, message: Dict[str, Any], channel: Optional[str] = None) -> int:
        """Broadcast JSON message to all clients or clients subscribed to a specific channel."""
        if channel:
            target_ids = list(self.channel_subscriptions.get(channel, set()))
        else:
            target_ids = list(self.active_connections.keys())

        sent_count = 0
        for connection_id in target_ids:
            success = await self.send_personal_message(message, connection_id)
            if success:
                sent_count += 1

        logger.debug(
            "Broadcasted message",
            channel=channel,
            recipient_count=sent_count,
            total_targets=len(target_ids),
        )
        return sent_count

    async def ping_all(self) -> None:
        """Send heartbeat ping frame to all active connections."""
        heartbeat_payload = {"type": "ping", "interval": settings.WS_HEARTBEAT_INTERVAL}
        await self.broadcast(heartbeat_payload)


# Global WebSocket connection manager instance
ws_manager = ConnectionManager()
