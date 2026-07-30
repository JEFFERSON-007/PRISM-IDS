"""Pytest Global Test Fixtures and Configurations."""

from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from app.core.config import Settings
from app.main import app


@pytest.fixture
def test_settings() -> Settings:
    """Fixture providing overridden test settings."""
    return Settings(
        ENVIRONMENT="testing",
        DEBUG=True,
        JWT_SECRET="test_secret_key_prism_ids_unit_tests_32bytes_long",
        POSTGRES_DB="prism_test_db",
    )


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP Client fixture bound to FastAPI app instance."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
