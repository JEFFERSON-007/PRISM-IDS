"""Asynchronous WebSocket Client for Persistent Server Real-Time Connection."""

import asyncio
import json
from typing import Callable, Optional, Dict, Any
import structlog
import websockets
from agent.core.config import agent_settings
from agent.core.state import agent_state

logger = structlog.get_logger("prism_agent.ws_client")


class AgentWebSocketClient:
    """Manages persistent WebSocket connection to PRISM Server with auto-reconnect."""

    def __init__(self, ws_url: Optional[str] = None) -> None:
        self._custom_ws_url = ws_url
        self._running: bool = False
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._message_handler: Optional[Callable[[Dict[str, Any]], None]] = None

    @property
    def ws_url(self) -> str:
        """Dynamic WebSocket URL evaluating active server settings."""
        return self._custom_ws_url or agent_settings.WS_URL or "ws://127.0.0.1:8000/ws/v1/connect"

    def set_message_handler(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        """Register a callback for incoming server WebSocket messages."""
        self._message_handler = handler

    async def start(self) -> None:
        """Start the persistent WebSocket loop in a background task."""
        self._running = True
        asyncio.create_task(self._connection_loop())

    async def stop(self) -> None:
        """Gracefully disconnect WebSocket client."""
        self._running = False
        if self._ws:
            try:
                await self._ws.close()
            except Exception:
                pass
        agent_state.websocket_connected = False
        logger.info("Stopped WebSocket client")

    async def _connection_loop(self) -> None:
        """Connection loop attempting reconnects on disconnect."""
        while self._running:
            try:
                url = self.ws_url
                logger.info("Connecting to PRISM Server WebSocket", url=url)
                async with websockets.connect(url) as ws:
                    self._ws = ws
                    agent_state.websocket_connected = True
                    logger.info("WebSocket connection established successfully")

                    while self._running:
                        message_str = await ws.recv()
                        try:
                            data = json.loads(message_str)
                            msg_type = data.get("type")

                            if msg_type == "ping":
                                await ws.send(json.dumps({"type": "pong", "timestamp": data.get("timestamp")}))
                            else:
                                logger.debug("Received WebSocket message", payload=data)
                                if self._message_handler:
                                    self._message_handler(data)

                        except json.JSONDecodeError:
                            logger.warning("Received invalid non-JSON WebSocket frame", raw=message_str)

            except (websockets.ConnectionClosedError, websockets.WebSocketException, OSError) as exc:
                agent_state.websocket_connected = False
                logger.warning(
                    "WebSocket connection lost or failed",
                    error=str(exc),
                    reconnect_in=agent_settings.RECONNECT_INTERVAL,
                )

            if self._running:
                await asyncio.sleep(agent_settings.RECONNECT_INTERVAL)
