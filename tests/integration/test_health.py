"""Integration tests for Health and System Status endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient) -> None:
    """Test /api/v1/health endpoint returning 200 OK and expected structure."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "database" in data
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time" in response.headers


@pytest.mark.asyncio
async def test_liveness_endpoint(async_client: AsyncClient) -> None:
    """Test /api/v1/health/liveness endpoint."""
    response = await async_client.get("/api/v1/health/liveness")
    assert response.status_code == 200
    data = response.json()
    assert data["alive"] is True


@pytest.mark.asyncio
async def test_system_status_endpoint(async_client: AsyncClient) -> None:
    """Test /api/v1/status endpoint."""
    response = await async_client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert "active_websocket_connections" in data
    assert "database_connected" in data
