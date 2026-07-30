"""Unit tests for FlowEngine lifecycle."""

import pytest
from agent.capture.packet_queue import PacketQueue
from agent.flow.flow_engine import FlowEngine


@pytest.mark.asyncio
async def test_flow_engine_start_stop() -> None:
    """Test FlowEngine initialization, binding, and lifecycle."""
    pkt_queue = PacketQueue()
    engine = FlowEngine()
    engine.bind_packet_queue(pkt_queue)

    await engine.start()
    status = engine.get_status()
    assert status["initialized"] is True
    assert status["running"] is True

    await engine.stop()
    status_after = engine.get_status()
    assert status_after["running"] is False
