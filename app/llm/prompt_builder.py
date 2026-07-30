"""Prompt Builder and Security Templates for LLM Analysis."""

import json
from typing import Any, Dict, List, Optional


class PromptBuilder:
    """Renders structured security prompts for LLM inference."""

    SYSTEM_SECURITY_ANALYST_PROMPT = (
        "You are an elite AI Security Analyst working in a Security Operations Center (SOC). "
        "Your duty is to explain network security alerts, assess risks, map threat vectors to MITRE ATT&CK, "
        "and provide actionable remediation advice to human SOC analysts. "
        "Base your analysis strictly on the provided structured IDS alert telemetry. "
        "Do NOT invent unverified facts. Return your response in valid JSON matching the specified structure."
    )

    @staticmethod
    def build_alert_analysis_prompt(context: Dict[str, Any]) -> str:
        """Render prompt requesting structured JSON threat analysis of a security alert."""
        context_str = json.dumps(context, indent=2)
        return f"""Analyze the following PRISM Intrusion Detection System security alert and generate a comprehensive security briefing.

[STRUCTURED ALERT TELEMETRY CONTEXT]
{context_str}

Please generate a JSON object with the following exact keys:
{{
  "executive_summary": "High-level 2-3 sentence overview for SOC leadership.",
  "technical_explanation": "Detailed technical explanation of attack mechanics and network behavior.",
  "trigger_rationale": "Why the Hybrid Detection Engine triggered this alert.",
  "risk_assessment": "Assessment of potential business risk and asset compromise.",
  "likely_impact": "Potential consequences if unmitigated.",
  "false_positive_indicators": ["List of indicators suggesting a potential false positive"],
  "mitre_attack_mapping": [
    {{
      "tactic": "Reconnaissance or Impact or Initial Access",
      "technique_id": "T1046",
      "technique_name": "Network Service Discovery",
      "description": "Explanation of mapping"
    }}
  ],
  "remediation_actions": [
    {{
      "priority": 1,
      "action_type": "BLOCK_IP",
      "title": "Block Source IP on Perimeter Firewall",
      "details": "Command or rule details"
    }}
  ]
}}
"""

    @staticmethod
    def build_chat_prompt(context: Optional[Dict[str, Any]], user_query: str, history: List[Dict[str, str]]) -> str:
        """Render prompt for interactive analyst Q&A session."""
        history_str = ""
        if history:
            history_str = "\n".join([f"{h['role'].upper()}: {h['content']}" for h in history[-6:]])

        context_str = json.dumps(context, indent=2) if context else "No specific alert selected."

        return f"""You are assisting a SOC Analyst with security questions regarding PRISM IDS.

[ACTIVE SECURITY TELEMETRY CONTEXT]
{context_str}

[CONVERSATION HISTORY]
{history_str}

[ANALYST QUESTION]
{user_query}

Provide a helpful, precise, and professional SOC answer based on the security context provided.
"""
