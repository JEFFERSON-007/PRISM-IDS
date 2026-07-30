"""Response Parser for LLM Structured Outputs."""

from datetime import datetime, timezone
import json
import re
from typing import Any, Dict, Optional
import structlog
from app.schemas.llm import LLMAnalysisResponse, MitreAttackMapping, RemediationAction

logger = structlog.get_logger("prism_ids.response_parser")


class ResponseParser:
    """Parses and validates raw LLM string output into structured Pydantic DTOs."""

    @staticmethod
    def parse_analysis_response(raw_text: str, alert_id: str, model_used: str) -> Optional[LLMAnalysisResponse]:
        """Extract and validate JSON response from LLM output string."""
        if not raw_text:
            return None

        # Clean markdown codeblock formatting if present
        cleaned_text = raw_text.strip()
        if "```json" in cleaned_text:
            cleaned_text = re.sub(r"^```json\s*", "", cleaned_text, flags=re.MULTILINE)
            cleaned_text = re.sub(r"```$", "", cleaned_text, flags=re.MULTILINE)
        elif "```" in cleaned_text:
            cleaned_text = re.sub(r"^```\s*", "", cleaned_text, flags=re.MULTILINE)
            cleaned_text = re.sub(r"```$", "", cleaned_text, flags=re.MULTILINE)

        try:
            data = json.loads(cleaned_text.strip())
            mitre_list = [
                MitreAttackMapping(**m) for m in data.get("mitre_attack_mapping", [])
            ]
            remediation_list = [
                RemediationAction(**r) for r in data.get("remediation_actions", [])
            ]

            return LLMAnalysisResponse(
                alert_id=alert_id,
                timestamp=datetime.now(timezone.utc),
                executive_summary=data.get("executive_summary", "Threat analysis completed."),
                technical_explanation=data.get("technical_explanation", "No detailed explanation provided."),
                trigger_rationale=data.get("trigger_rationale", "Alert triggered by PRISM Hybrid Engine."),
                risk_assessment=data.get("risk_assessment", "Standard risk evaluation applied."),
                likely_impact=data.get("likely_impact", "Potential network disruption."),
                false_positive_indicators=data.get("false_positive_indicators", []),
                mitre_attack_mapping=mitre_list,
                remediation_actions=remediation_list,
                generated_by_model=model_used,
            )
        except Exception as exc:
            logger.error("Failed to parse LLM JSON output", error=str(exc), raw_snippet=raw_text[:200])

        return None
