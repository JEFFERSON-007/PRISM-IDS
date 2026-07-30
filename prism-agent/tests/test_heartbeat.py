"""Unit tests for heartbeat service."""

from unittest.mock import AsyncMock, MagicMock
import pytest
from agent.heartbeat.service import HeartbeatDaemonService


@pytest.mark.asyncio
async def test_heartbeat_transmission_cycle() -> None:
    """Test heartbeat daemon transmission cycle."""
    mock_http = MagicMock()
    mock_http.post = AsyncMock(return_value={"status": "ok"})

    service = HeartbeatDaemonService(http_client=mock_http)
    await service.start()
    assert service._running is True
    await service.stop()
    assert service._running is False
