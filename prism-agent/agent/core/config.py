"""Agent Pydantic Settings Configuration."""

from typing import Optional
from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    """Core settings for PRISM IDS agent daemon."""

    model_config = SettingsConfigDict(
        env_file=".env.agent",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Central Server Connection Configuration
    SERVER_URL: str = Field(default="http://localhost:8000", description="PRISM Central Server HTTP base URL")
    WS_URL: Optional[str] = Field(default=None, description="PRISM Central Server WebSocket URL")

    @field_validator("WS_URL", mode="before")
    def assemble_ws_url(cls, v: Optional[str], info: ValidationInfo) -> str:
        """Dynamically derive WebSocket URL from SERVER_URL if not explicitly configured."""
        if isinstance(v, str) and v.strip():
            return v
        server_url = info.data.get("SERVER_URL", "http://localhost:8000")
        clean_url = server_url.rstrip("/")
        if clean_url.startswith("https://"):
            base_ws = clean_url.replace("https://", "wss://")
        elif clean_url.startswith("http://"):
            base_ws = clean_url.replace("http://", "ws://")
        else:
            base_ws = f"ws://{clean_url}"
        return f"{base_ws}/ws/v1/connect"

    # Agent Identification
    AGENT_NAME: str = Field(default="agent-node-01", description="Unique human-readable agent name")
    AGENT_VERSION: str = Field(default="1.0.0", description="Agent software version")

    # Local Credentials Storage
    CREDENTIALS_FILE: str = Field(
        default=".agent_credentials.json", description="Local path for storing credentials"
    )

    # Operational Parameters
    HEARTBEAT_INTERVAL: int = Field(default=15, description="Heartbeat transmission interval in seconds")
    RECONNECT_INTERVAL: int = Field(default=5, description="WebSocket reconnect delay in seconds")
    HTTP_TIMEOUT: float = Field(default=10.0, description="HTTP request timeout in seconds")

    # Packet Capture Subsystem Parameters
    CAPTURE_ENABLED: bool = Field(default=True, description="Enable real-time packet capture engine")
    CAPTURE_INTERFACE: Optional[str] = Field(default=None, description="Network interface name to capture on")
    BPF_FILTER: str = Field(default="ip or ip6", description="Berkeley Packet Filter string")
    PROMISCUOUS_MODE: bool = Field(default=True, description="Enable promiscuous capture mode")
    BUFFER_SIZE: int = Field(default=1048576, description="Packet capture buffer size in bytes")
    QUEUE_MAX_SIZE: int = Field(default=10000, description="Maximum packets in async processing queue")
    PACKET_LIMIT: int = Field(default=0, description="Maximum packets to capture (0 = unlimited)")
    CAPTURE_BACKEND: str = Field(default="scapy", description="Packet capture backend driver")

    # Flow Generation Engine Parameters
    FLOW_ENABLED: bool = Field(default=True, description="Enable flow generation engine")
    FLOW_IDLE_TIMEOUT: float = Field(default=15.0, description="Flow idle timeout in seconds")
    FLOW_ACTIVE_TIMEOUT: float = Field(default=120.0, description="Flow maximum active lifetime in seconds")
    FLOW_CLEANUP_INTERVAL: float = Field(default=5.0, description="Flow table expiration cleanup interval in seconds")
    FLOW_TABLE_MAX_SIZE: int = Field(default=50000, description="Maximum concurrent active flows in table")
    FLOW_QUEUE_MAX_SIZE: int = Field(default=10000, description="Maximum completed flows in output queue")

    # Feature Extraction Engine Parameters
    FEATURE_EXTRACTION_ENABLED: bool = Field(default=True, description="Enable feature extraction engine")
    FEATURE_ENTROPY_ENABLED: bool = Field(default=True, description="Enable Shannon entropy calculations")
    FEATURE_VALIDATION_STRICT: bool = Field(default=False, description="Strict validation rejecting non-compliant vectors")
    FEATURE_BATCH_SIZE: int = Field(default=100, description="Batch processing size for feature extraction")
    FEATURE_QUEUE_MAX_SIZE: int = Field(default=10000, description="Maximum feature vectors in output queue")

    # Hybrid Intrusion Detection Engine Parameters
    DETECTION_ENABLED: bool = Field(default=True, description="Enable hybrid intrusion detection engine")
    SIGNATURE_ENGINE_ENABLED: bool = Field(default=True, description="Enable signature-based rule engine")
    ML_ENGINE_ENABLED: bool = Field(default=True, description="Enable machine learning detection engine")
    MODEL_PATH: str = Field(default="models/prism_ids_rf.joblib", description="Path to pre-trained ML model file")
    RULE_FILE_PATH: str = Field(default="rules/signature_rules.json", description="Path to signature rules JSON file")
    CONFIDENCE_THRESHOLD: float = Field(default=0.5, description="Minimum confidence threshold for valid detection")
    ML_PREDICTION_THRESHOLD: float = Field(default=0.6, description="ML malicious probability threshold")
    DETECTION_QUEUE_MAX_SIZE: int = Field(default=10000, description="Maximum detection results in output queue")

    # Risk Engine & Alert Management Parameters
    RISK_ENGINE_ENABLED: bool = Field(default=True, description="Enable risk engine and alert management")
    RISK_THRESHOLD_INFORMATIONAL: float = Field(default=0.0, description="Informational severity lower bound")
    RISK_THRESHOLD_LOW: float = Field(default=20.0, description="Low severity lower bound")
    RISK_THRESHOLD_MEDIUM: float = Field(default=40.0, description="Medium severity lower bound")
    RISK_THRESHOLD_HIGH: float = Field(default=70.0, description="High severity lower bound")
    RISK_THRESHOLD_CRITICAL: float = Field(default=90.0, description="Critical severity lower bound")
    ALERT_DEDUP_WINDOW: float = Field(default=60.0, description="Alert deduplication time window in seconds")
    ALERT_QUEUE_MAX_SIZE: int = Field(default=10000, description="Maximum outbound alerts in queue")
    ALERT_MAX_RETRIES: int = Field(default=5, description="Maximum alert transmission retry attempts")
    ALERT_RETRY_BACKOFF: float = Field(default=2.0, description="Initial retry backoff delay in seconds")

    # Logging & Environment
    LOG_LEVEL: str = Field(default="INFO", description="Log level (DEBUG, INFO, WARNING, ERROR)")
    LOG_FORMAT: str = Field(default="json", description="Log format (json or console)")
    LOG_DIR: str = Field(default="logs", description="Local log directory")
    DEBUG: bool = Field(default=True, description="Enable debug logging")
    TIMEZONE: str = Field(default="UTC", description="Default timezone")


agent_settings = AgentSettings()
