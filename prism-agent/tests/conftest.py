"""Pytest fixtures for PRISM Agent suite."""

import pytest
from agent.core.config import AgentSettings


@pytest.fixture
def mock_agent_settings() -> AgentSettings:
    """Fixture providing test settings."""
    return AgentSettings(
        AGENT_NAME="test-agent-node",
        SERVER_URL="http://mock-server:8000",
        HEARTBEAT_INTERVAL=5,
    )
