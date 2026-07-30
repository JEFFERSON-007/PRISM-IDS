"""Unit tests for HybridEngine lifecycle."""

import pytest
from agent.detection.hybrid_engine import HybridEngine
from agent.feature_extraction.feature_queue import FeatureQueue


@pytest.mark.asyncio
async def test_hybrid_engine_start_stop() -> None:
    """Test HybridEngine binding and lifecycle."""
    feature_q = FeatureQueue()
    engine = HybridEngine()
    engine.bind_feature_queue(feature_q)

    await engine.start()
    status = engine.get_status()
    assert status["initialized"] is True
    assert status["running"] is True

    await engine.stop()
    status_after = engine.get_status()
    assert status_after["running"] is False
