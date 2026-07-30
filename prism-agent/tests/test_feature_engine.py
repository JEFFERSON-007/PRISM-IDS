"""Unit tests for FeatureEngine lifecycle."""

import pytest
from agent.feature_extraction.feature_engine import FeatureEngine
from agent.flow.flow_queue import FlowQueue


@pytest.mark.asyncio
async def test_feature_engine_start_stop() -> None:
    """Test FeatureEngine binding and lifecycle."""
    flow_q = FlowQueue()
    engine = FeatureEngine()
    engine.bind_flow_queue(flow_q)

    await engine.start()
    status = engine.get_status()
    assert status["initialized"] is True
    assert status["running"] is True

    await engine.stop()
    status_after = engine.get_status()
    assert status_after["running"] is False
