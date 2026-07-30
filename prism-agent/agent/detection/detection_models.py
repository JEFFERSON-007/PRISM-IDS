"""Detection Data Models and Result Specifications."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


class SeverityEnum(str, Enum):
    """Detection severity rating."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DetectionMethodEnum(str, Enum):
    """Detection mechanism type."""

    SIGNATURE = "SIGNATURE"
    MACHINE_LEARNING = "MACHINE_LEARNING"
    HYBRID = "HYBRID"


class RuleDefinition(BaseModel):
    """Signature Rule specification."""

    rule_id: str
    name: str
    description: str
    severity: SeverityEnum
    protocol: str = "ANY"
    enabled: bool = True
    conditions: Dict[str, Any]
    action: str = "ALERT"


class RuleMatch(BaseModel):
    """Matched Signature Rule details."""

    rule_id: str
    name: str
    severity: SeverityEnum
    evidence: Dict[str, Any]


class MLPredictionResult(BaseModel):
    """Machine Learning model inference prediction result."""

    is_malicious: bool
    probability: float = Field(ge=0.0, le=1.0)
    model_name: str = Field(default="RandomForestClassifier")
    confidence: float = Field(ge=0.0, le=1.0)


class DetectionResult(BaseModel):
    """Unified standardized output payload from Hybrid Detection Engine."""

    detection_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    flow_id: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str

    detection_method: DetectionMethodEnum
    matched_rules: List[RuleMatch] = Field(default_factory=list)
    ml_prediction: Optional[MLPredictionResult] = None

    confidence_score: float = Field(ge=0.0, le=1.0)
    severity: SeverityEnum
    evidence: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="DETECTED")
