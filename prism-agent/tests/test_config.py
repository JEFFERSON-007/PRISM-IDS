"""Unit tests for agent settings configuration."""

from agent.core.config import AgentSettings


def test_agent_config_defaults() -> None:
    """Test default agent configuration options."""
    settings = AgentSettings()
    assert settings.AGENT_VERSION == "1.0.0"
    assert settings.HEARTBEAT_INTERVAL == 15
    assert settings.CREDENTIALS_FILE == ".agent_credentials.json"
