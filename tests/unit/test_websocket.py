"""Unit tests for WebSocket ConnectionManager."""

import pytest
from unittest.mock import AsyncMock
from app.websocket.manager import ConnectionManager


@pytest.mark.asyncio
async def test_websocket_manager_lifecycle() -> None:
    """Test connect, disconnect, and total connections counter."""
    manager = ConnectionManager()
    assert manager.total_connections == 0

    mock_ws = AsyncMock()
    mock_ws.accept = AsyncMock()

    conn_id = "test-conn-1"
    connected = await manager.connect(conn_id, mock_ws)
    assert connected is True
    assert manager.total_connections == 1

    await manager.subscribe(conn_id, "alerts")
    assert "alerts" in manager.channel_subscriptions

    await manager.disconnect(conn_id)
    assert manager.total_connections == 0
    assert conn_id not in manager.channel_subscriptions.get("alerts", set())
