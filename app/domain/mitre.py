"""MITRE ATT&CK Framework Mapping Engine and Domain Catalog."""

from typing import Any, Dict, List, Optional


class MitreAttackCatalog:
    """Catalog of MITRE ATT&CK Tactics, Techniques, and Mitigation Mapping Rules."""

    TECHNIQUES: Dict[str, Dict[str, Any]] = {
        "T1046": {
            "tactic": "Reconnaissance",
            "technique_id": "T1046",
            "technique_name": "Network Service Discovery",
            "description": "Adversaries may attempt to get a listing of services running on remote hosts to identify vulnerable targets.",
            "recommended_defenses": "Implement egress port filtering, monitor unusual SYN scan volume, and employ network rate limiting.",
        },
        "T1110": {
            "tactic": "Credential Access",
            "technique_id": "T1110",
            "technique_name": "Brute Force",
            "description": "Adversaries may use brute force techniques to gain access to accounts by systematically guessing passwords.",
            "recommended_defenses": "Enforce strong password policies, implement account lockout thresholds, and use multi-factor authentication.",
        },
        "T1498": {
            "tactic": "Impact",
            "technique_id": "T1498",
            "technique_name": "Network Denial of Service",
            "description": "Adversaries may perform Network Denial of Service (DoS) attacks to degrade or disrupt service availability.",
            "recommended_defenses": "Deploy upstream scrubbing services, configure TCP SYN cookies, and enforce rate limits.",
        },
        "T1071": {
            "tactic": "Command and Control",
            "technique_id": "T1071",
            "technique_name": "Application Layer Protocol",
            "description": "Adversaries may communicate using application layer protocols (HTTP, HTTPS, DNS) to blend in with normal network traffic.",
            "recommended_defenses": "Inspect SSL/TLS certificate metadata, enforce deep packet inspection, and restrict outbound protocols.",
        },
        "T1059": {
            "tactic": "Execution",
            "technique_id": "T1059",
            "technique_name": "Command and Scripting Interpreter",
            "description": "Adversaries may abuse command and script interpreters to execute arbitrary commands.",
            "recommended_defenses": "Restrict script execution policies, log command line arguments, and deploy Endpoint Detection Response (EDR).",
        },
    }

    @classmethod
    def get_matrix(cls) -> List[Dict[str, Any]]:
        """Return full MITRE ATT&CK technique catalog."""
        return list(cls.TECHNIQUES.values())

    @classmethod
    def map_alert_telemetry(cls, dst_port: int, protocol: str, severity: str, matched_rules: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Map alert 5-tuple and signature rule evidence to MITRE ATT&CK techniques."""
        mappings: List[Dict[str, Any]] = []

        if dst_port in [80, 443]:
            mappings.append(cls.TECHNIQUES["T1046"])
            mappings.append(cls.TECHNIQUES["T1071"])
        elif dst_port in [22, 3389, 5432]:
            mappings.append(cls.TECHNIQUES["T1110"])
        else:
            mappings.append(cls.TECHNIQUES["T1498"])

        return mappings
