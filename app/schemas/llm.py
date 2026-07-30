"""Pydantic Schemas for AI Security Analyst (LLM Integration)."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AlertAnalysisRequest(BaseModel):
    """Request schema for AI Alert Analysis."""

    alert_id: Optional[str] = Field(None, description="String alert_id or UUID to fetch from database")
    alert_payload: Optional[Dict[str, Any]] = Field(None, description="Raw Alert DTO payload if not in database")


class MitreAttackMapping(BaseModel):
    """MITRE ATT&CK Framework Mapping Suggestion."""

    tactic: str = Field(description="Tactical category (e.g. Reconnaissance, Persistence, Privilege Escalation)")
    technique_id: str = Field(description="MITRE Technique ID (e.g. T1046, T1498)")
    technique_name: str = Field(description="Human readable technique title")
    description: str = Field(description="Why this security alert maps to this MITRE technique")


class RemediationAction(BaseModel):
    """Prioritized Remediation Action."""

    priority: int = Field(description="Action priority (1 = Immediate, 2 = Short-term, 3 = Long-term)")
    action_type: str = Field(description="Category (e.g. BLOCK_IP, ISOLATE_HOST, CAPTURE_PCAP, RECONFIGURE_FIREWALL)")
    title: str = Field(description="Brief action title")
    details: str = Field(description="Technical execution instructions for SOC analyst")


class LLMAnalysisResponse(BaseModel):
    """Structured AI Security Analyst Response Briefing."""

    alert_id: str
    timestamp: datetime
    executive_summary: str = Field(description="High-level 2-3 sentence overview for SOC leadership")
    technical_explanation: str = Field(description="Detailed technical breakdown of attack mechanics")
    trigger_rationale: str = Field(description="Why the Hybrid Detection Engine triggered this alert")
    risk_assessment: str = Field(description="Assessment of business and infrastructure risk")
    likely_impact: str = Field(description="Potential consequences if unmitigated")
    false_positive_indicators: List[str] = Field(default_list=[], description="Indicators suggesting a possible false positive")
    mitre_attack_mapping: List[MitreAttackMapping] = Field(default_list=[], description="Suggested MITRE ATT&CK mappings")
    remediation_actions: List[RemediationAction] = Field(default_list=[], description="Prioritized mitigation steps")
    generated_by_model: str = Field(description="LLM model identifier or fallback generator")


class ChatMessageRequest(BaseModel):
    """Request schema for SOC Analyst Q&A Chat."""

    session_id: str = Field(description="Unique conversation session UUID")
    message: str = Field(min_length=1, max_length=2000, description="Analyst question or query")
    alert_id: Optional[str] = Field(None, description="Optional alert ID context")


class ChatMessageResponse(BaseModel):
    """Response schema for SOC Analyst Q&A Chat."""

    session_id: str
    reply: str
    timestamp: datetime
    model_used: str


class LLMHealthResponse(BaseModel):
    """LLM Service Health & Connectivity Schema."""

    status: str = Field(description="HEALTHY, DEGRADED, or OFFLINE")
    ollama_url: str
    configured_model: str
    ollama_online: bool
    available_models: List[str] = Field(default_list=[])
