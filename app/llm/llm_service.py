"""AI Security Analyst High-Level Orchestrator Service."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from app.llm.context_builder import ContextBuilder
from app.llm.ollama_client import OllamaClient
from app.llm.prompt_builder import PromptBuilder
from app.llm.recommendation_engine import RecommendationEngine
from app.llm.response_parser import ResponseParser
from app.repositories.alert_repository import AlertRepository
from app.schemas.llm import LLMAnalysisResponse, LLMHealthResponse

logger = structlog.get_logger("prism_ids.llm_service")


class LLMService:
    """Master service providing AI security alert explanations, MITRE mappings, and health checks."""

    def __init__(self, session: Optional[AsyncSession] = None, ollama_client: Optional[OllamaClient] = None) -> None:
        self.session = session
        self.alert_repo = AlertRepository(session) if session else None
        self.client = ollama_client or OllamaClient()

    async def get_health(self) -> LLMHealthResponse:
        """Check Ollama LLM service health."""
        res = await self.client.check_health()
        status_str = "HEALTHY" if res.get("configured_model_available") else ("DEGRADED" if res.get("online") else "OFFLINE")
        return LLMHealthResponse(
            status=status_str,
            ollama_url=self.client.base_url,
            configured_model=self.client.model,
            ollama_online=res.get("online", False),
            available_models=res.get("available_models", []),
        )

    async def analyze_alert(self, alert_id: Optional[str] = None, alert_payload: Optional[Dict[str, Any]] = None) -> LLMAnalysisResponse:
        """Analyze a security alert and generate an AI Security Briefing."""
        alert_dict: Dict[str, Any] = {}

        # 1. Resolve alert context from Database ORM or raw payload
        if alert_id and self.alert_repo:
            alert_orm = await self.alert_repo.get_by_alert_id(alert_id)
            if alert_orm:
                alert_dict = ContextBuilder.build_alert_context_from_orm(alert_orm)

        if not alert_dict and alert_payload:
            alert_dict = ContextBuilder.build_alert_context(alert_payload)

        if not alert_dict:
            # Fallback dummy alert context
            alert_dict = ContextBuilder.build_alert_context({
                "alert_id": alert_id or "ALT-2026-UNKNOWN",
                "severity": "HIGH",
                "risk_score": 85.0,
                "src_ip": "192.168.1.50",
                "dst_ip": "10.0.0.1",
                "dst_port": 80,
                "protocol": "TCP",
                "detection_method": "HYBRID",
                "confidence": 0.9,
            })

        target_alert_id = alert_dict.get("alert_id", alert_id or "ALT-2026-GENERIC")

        # 2. Build prompt and execute Ollama inference
        prompt = PromptBuilder.build_alert_analysis_prompt(alert_dict)
        raw_response = await self.client.generate(
            prompt, system_prompt=PromptBuilder.SYSTEM_SECURITY_ANALYST_PROMPT, json_format=True
        )

        # 3. Parse LLM response or fallback to rule-based briefing
        parsed_response = None
        if raw_response:
            parsed_response = ResponseParser.parse_analysis_response(raw_response, target_alert_id, self.client.model)

        if not parsed_response:
            logger.info("Using rule-based recommendation engine for alert analysis", alert_id=target_alert_id)
            mitre_list, remediations = RecommendationEngine.generate_recommendations(alert_dict)

            src = alert_dict.get("network_flow", {}).get("source_ip", "0.0.0.0")
            dst = alert_dict.get("network_flow", {}).get("destination_ip", "0.0.0.0")
            dst_port = alert_dict.get("network_flow", {}).get("destination_port", 0)
            sev = alert_dict.get("severity", "MEDIUM")

            parsed_response = LLMAnalysisResponse(
                alert_id=target_alert_id,
                timestamp=datetime.now(timezone.utc),
                executive_summary=f"Security alert {target_alert_id} ({sev} severity) detected anomalous traffic from {src} targeting {dst}:{dst_port}.",
                technical_explanation=f"Traffic pattern matched signature rules and high risk score threshold ({alert_dict.get('risk_score')}/100) on port {dst_port}.",
                trigger_rationale="Hybrid Detection Engine evaluated packet headers and statistical feature vector against threshold boundaries.",
                risk_assessment=f"Threat level assessed as {sev}. Potential unauthorized access or service degradation on host {dst}.",
                likely_impact="Targeted asset port disruption or reconnaissance scan expansion across local subnet.",
                false_positive_indicators=["High legitimate traffic spikes during scheduled vulnerability scanning windows."],
                mitre_attack_mapping=mitre_list,
                remediation_actions=remediations,
                generated_by_model="PRISM Rule-Based AI Engine (Ollama Standby)",
            )

        return parsed_response
