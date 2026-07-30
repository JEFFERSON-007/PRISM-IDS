"""Standardized Alert Data Model and Status Specification."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field
from agent.detection.detection_models import DetectionMethodEnum, MLPredictionResult, RuleMatch, SeverityEnum


class AlertStatusEnum(str, Enum):
    """Alert resolution status."""

    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


class Alert(BaseModel):
    """Actionable security alert object delivered to PRISM Server."""

    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    detection_id: str
    agent_id: str
    flow_id: str

    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str

    risk_score: float = Field(ge=0.0, le=100.0)
    severity: SeverityEnum
    detection_method: DetectionMethodEnum

    matched_rules: List[RuleMatch] = Field(default_factory=list)
    ml_prediction: Optional[MLPredictionResult] = None
    confidence: float = Field(ge=0.0, le=1.0)

    evidence_summary: Dict[str, Any] = Field(default_factory=dict)
    status: AlertStatusEnum = AlertStatusEnum.OPEN
    occurrence_count: int = Field(default=1, ge=1)
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert Alert to JSON-serializable dictionary."""
        return self.model_dump(mode="json")
