"""Application Configuration powered by Pydantic Settings."""

from typing import List, Literal
from pydantic import Field, PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Core settings model loading values from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # General Application Info
    APP_NAME: str = Field(default="PRISM IDS Server", description="Name of the application")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    ENVIRONMENT: Literal["development", "testing", "production"] = Field(
        default="development", description="Execution environment"
    )
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    SERVER_HOST: str = Field(default="0.0.0.0", description="Server host bind address")
    SERVER_PORT: int = Field(default=8000, description="Server port bind address")
    API_V1_STR: str = Field(default="/api/v1", description="Global API v1 prefix")
    TIMEZONE: str = Field(default="UTC", description="Application default timezone")

    # Database Settings
    POSTGRES_SERVER: str = Field(default="localhost", description="Database host")
    POSTGRES_PORT: int = Field(default=5432, description="Database port")
    POSTGRES_USER: str = Field(default="prism_user", description="Database username")
    POSTGRES_PASSWORD: str = Field(default="prism_secure_password", description="Database password")
    POSTGRES_DB: str = Field(default="prism_ids_db", description="Database name")
    DATABASE_URL: str | None = Field(
        default=None, description="Async PostgreSQL SQLAlchemy connection string"
    )
    DB_POOL_SIZE: int = Field(default=10, description="SQLAlchemy connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="SQLAlchemy max pool overflow")
    DB_POOL_TIMEOUT: int = Field(default=30, description="SQLAlchemy connection pool timeout")

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> str:
        """Construct database URL if not directly supplied in env."""
        if isinstance(v, str) and v.strip():
            return v
        values = info.data
        user = values.get("POSTGRES_USER")
        password = values.get("POSTGRES_PASSWORD")
        host = values.get("POSTGRES_SERVER")
        port = values.get("POSTGRES_PORT")
        db = values.get("POSTGRES_DB")
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

    # JWT Authentication Settings
    JWT_SECRET: str = Field(
        default="prism_dev_secret_key_change_in_production_32bytes_minimum_length",
        description="Secret key for signing JWT tokens",
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token expiration in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, description="Refresh token expiration in days"
    )

    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO", description="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    LOG_FORMAT: str = Field(default="json", description="Log format (json or console)")
    LOG_DIR: str = Field(default="logs", description="Directory for rotating log files")

    # Security & CORS Settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://localhost:5173"],
        description="Allowed origins for CORS",
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["*"], description="Allowed HTTP host headers"
    )

    # WebSocket Infrastructure Settings
    WS_HEARTBEAT_INTERVAL: int = Field(
        default=30, description="WebSocket heartbeat ping interval in seconds"
    )
    WS_MAX_CONNECTIONS: int = Field(
        default=1000, description="Maximum concurrent WebSocket connections"
    )

    # LLM / Ollama AI Analyst Settings
    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434", description="Ollama local LLM API service URL"
    )
    OLLAMA_MODEL: str = Field(
        default="qwen:3b", description="Target LLM model identifier (e.g. qwen:3b, llama3.2)"
    )
    OLLAMA_TIMEOUT_SECONDS: int = Field(
        default=30, description="Timeout in seconds for LLM inference HTTP requests"
    )
    LLM_ENABLED: bool = Field(
        default=True, description="Master toggle for AI Security Analyst LLM integration"
    )


# Global settings instance
settings = Settings()
