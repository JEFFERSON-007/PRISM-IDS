"""Pydantic Schemas for AI Security Analyst Integration."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AIHealthResponse(BaseModel):
    """Health check response schema for Ollama AI Analyst."""

    online: bool
    model_name: str
    model_available: bool
    loaded: bool
    available_models: List[str] = Field(default_factory=list)


class AIAlertSummaryRequest(BaseModel):
    """Request payload for alert summary endpoint."""

    alert_id: str


class AIAlertSummaryResponse(BaseModel):
    """Response payload containing AI alert analysis summary."""

    alert_id: str
    executive_summary: str
    technical_explanation: str
    trigger_rationale: str
    risk_assessment: str
    likely_impact: str
    false_positive_indicators: List[str] = Field(default_factory=list)
    mitre_attack_mapping: List[Dict[str, Any]] = Field(default_factory=list)
    remediation_actions: List[Dict[str, Any]] = Field(default_factory=list)
    investigation_steps: List[str] = Field(default_factory=list)
    cached: bool = False
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class AIChatRequest(BaseModel):
    """Request payload for AI Chat endpoint."""

    prompt: str = Field(..., description="User query or instruction")
    alert_id: Optional[str] = Field(default=None, description="Optional alert context ID")
    stream: bool = Field(default=False, description="Enable chunked streaming response")


class AIChatResponse(BaseModel):
    """Response payload for AI Chat endpoint when stream=False."""

    response: str
    context_used: Optional[Dict[str, Any]] = None
    model: str = "qwen2.5:3b"
    latency_ms: float = 0.0


class AIReportRequest(BaseModel):
    """Request payload for Executive Report generation."""

    timeframe: Optional[str] = Field(default="24h", description="Time window for report (e.g. 24h, 7d)")
    top_limit: Optional[int] = Field(default=5, description="Limit for top attacks/assets")


class AIReportResponse(BaseModel):
    """Executive Security Report response schema."""

    executive_summary: str
    top_attacks: List[Dict[str, Any]] = Field(default_factory=list)
    most_targeted_assets: List[Dict[str, Any]] = Field(default_factory=list)
    common_mitre_techniques: List[Dict[str, Any]] = Field(default_factory=list)
    risk_trends: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
