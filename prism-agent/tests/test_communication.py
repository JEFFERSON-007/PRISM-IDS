"""Unit tests for agent HTTP client headers."""

from agent.communication.http_client import AgentHTTPClient


def test_agent_http_client_headers() -> None:
    """Test header construction with credentials."""
    client = AgentHTTPClient(base_url="http://test-server:8000")
    client.set_credentials("agent-uuid-123", "secret-key-456")

    headers = client._get_headers()
    assert headers["X-Agent-ID"] == "agent-uuid-123"
    assert headers["X-Agent-Secret"] == "secret-key-456"
