"""Pydantic Schemas for Alert Data Validation and Ingestion."""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    """Schema for alert ingestion payload from PRISM Agent."""

    alert_id: str
    timestamp: datetime
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None

    detection_id: str
    agent_id: Optional[str] = None
    flow_id: str

    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str

    risk_score: float = Field(ge=0.0, le=100.0)
    severity: str
    detection_method: str

    matched_rules: Optional[List[Dict[str, Any]]] = None
    ml_prediction: Optional[Dict[str, Any]] = None
    confidence: float = Field(ge=0.0, le=1.0)

    evidence_summary: Optional[Dict[str, Any]] = None
    status: str = "OPEN"
    occurrence_count: int = 1
    correlation_id: Optional[str] = None


class AlertRead(BaseModel):
    """Schema for alert API response payload."""

    id: uuid.UUID
    alert_id: str
    timestamp: datetime
    first_seen: datetime
    last_seen: datetime

    detection_id: str
    agent_id: Optional[uuid.UUID] = None
    flow_id: str

    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str

    risk_score: float
    severity: str
    detection_method: str

    matched_rules: Optional[List[Dict[str, Any]]] = None
    ml_prediction: Optional[Dict[str, Any]] = None
    confidence: float

    evidence_summary: Optional[Dict[str, Any]] = None
    status: str
    occurrence_count: int
    correlation_id: Optional[str] = None

    class Config:
        from_attributes = True


class AlertPaginationResponse(BaseModel):
    """Paginated list of alerts."""

    items: List[AlertRead]
    page: int
    page_size: int
    total_records: int
    total_pages: int
