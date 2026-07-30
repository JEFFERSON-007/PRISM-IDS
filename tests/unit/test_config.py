"""Unit tests for Pydantic Settings Application Configuration."""

from app.core.config import Settings


def test_default_settings_values() -> None:
    """Verify default setting properties."""
    settings = Settings()
    assert settings.APP_NAME == "PRISM IDS Server"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.SERVER_PORT == 8000
    assert "postgresql+asyncpg://" in settings.DATABASE_URL
