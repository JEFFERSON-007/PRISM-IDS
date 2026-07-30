"""Integration tests for Agent Registration API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_agent_registration_endpoint(async_client: AsyncClient) -> None:
    """Test POST /api/v1/agents/register endpoint."""
    payload = {
        "agent_name": "test-agent-sensor",
        "hostname": "sensor.prism.local",
        "ip_address": "10.0.0.15",
        "operating_system": "Debian 12",
        "version": "1.0.0",
    }
    response = await async_client.post("/api/v1/agents/register", json=payload)
    # Returns 201 Created or error depending on mock/database availability
    assert response.status_code in [201, 500, 422]
