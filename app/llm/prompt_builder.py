"""Prompt Builder and Security Templates for LLM Analysis."""

import json
from typing import Any, Dict, List, Optional


class PromptBuilder:
    """Renders structured security prompts for LLM inference."""

    SYSTEM_SECURITY_ANALYST_PROMPT = (
        "You are a Senior SOC Level-3 Cybersecurity Analyst. "
        "The attack has already been detected. "
        "Never decide whether traffic is malicious. "
        "Your role is only to explain and recommend."
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
      "tactic": "Reconnaissance or Credential Access or Initial Access or Impact",
      "technique_id": "T1110 or T1190 or T1046",
      "technique_name": "Brute Force or Exploit Public-Facing Application or Network Service Discovery",
      "description": "Short explanation of mapping"
    }}
  ],
  "remediation_actions": [
    {{
      "priority": 1,
      "action_type": "BLOCK_IP",
      "title": "Block Source IP on Perimeter Firewall",
      "details": "Command or rule details"
    }}
  ],
  "investigation_steps": [
    "Step 1: Check firewall logs for additional source IP traffic.",
    "Step 2: Inspect target host for file modifications."
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

    @staticmethod
    def build_executive_report_prompt(incidents_summary: Dict[str, Any], alerts_summary: Dict[str, Any], network_summary: Dict[str, Any]) -> str:
        """Render prompt requesting structured JSON executive security report."""
        incidents_str = json.dumps(incidents_summary, indent=2)
        alerts_str = json.dumps(alerts_summary, indent=2)
        network_str = json.dumps(network_summary, indent=2)

        return f"""Generate an Executive SOC Security Report for organizational leadership based on the following telemetry summaries.

[INCIDENTS TELEMETRY]
{incidents_str}

[ALERTS TELEMETRY]
{alerts_str}

[NETWORK & AGENT METRICS]
{network_str}

Please generate a JSON object with the following exact keys:
{{
  "executive_summary": "High-level summary of security posture, active threats, and key metrics.",
  "top_attacks": [
    {{"attack_type": "Port Scanning", "count": 42, "severity": "HIGH"}}
  ],
  "most_targeted_assets": [
    {{"destination_ip": "10.0.0.1", "alert_count": 15, "highest_severity": "CRITICAL"}}
  ],
  "common_mitre_techniques": [
    {{"technique_id": "T1046", "technique_name": "Network Service Discovery", "count": 25}}
  ],
  "risk_trends": [
    {{"metric": "Average Risk Score", "value": "68.4", "status": "STABLE"}}
  ],
  "recommendations": [
    "Implement perimeter rate-limiting for ICMP/SYN sweeps",
    "Isolate untrusted agent subnets"
  ]
}}
"""
