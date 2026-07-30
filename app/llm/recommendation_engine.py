"""Recommendation Engine for Prioritized Security Actions."""

from typing import Any, Dict, List, Tuple
from app.schemas.llm import MitreAttackMapping, RemediationAction


class RecommendationEngine:
    """Generates prioritized security remediation recommendations based on alert risk."""

    @staticmethod
    def generate_recommendations(alert_context: Dict[str, Any]) -> Tuple[List[MitreAttackMapping], List[RemediationAction]]:
        """Generate rule-based fallback MITRE mappings and remediation steps."""
        severity = alert_context.get("severity", "MEDIUM").upper()
        src_ip = alert_context.get("network_flow", {}).get("source_ip", "0.0.0.0")
        dst_ip = alert_context.get("network_flow", {}).get("destination_ip", "0.0.0.0")
        dst_port = alert_context.get("network_flow", {}).get("destination_port", 0)

        mitre_mappings: List[MitreAttackMapping] = []
        remediations: List[RemediationAction] = []

        # 1. MITRE ATT&CK Mapping
        if dst_port in [80, 443]:
            mitre_mappings.append(
                MitreAttackMapping(
                    tactic="Initial Access / Reconnaissance",
                    technique_id="T1046",
                    technique_name="Network Service Discovery",
                    description=f"Attacker scanned or targeted web service port {dst_port} from {src_ip}.",
                )
            )
        elif dst_port in [22, 3389]:
            mitre_mappings.append(
                MitreAttackMapping(
                    tactic="Credential Access",
                    technique_id="T1110",
                    technique_name="Brute Force",
                    description=f"Attacker targeted remote access service on port {dst_port}.",
                )
            )
        else:
            mitre_mappings.append(
                MitreAttackMapping(
                    tactic="Impact",
                    technique_id="T1498",
                    technique_name="Network Denial of Service",
                    description=f"High rate of anomalous traffic directed to {dst_ip}:{dst_port}.",
                )
            )

        # 2. Prioritized Remediation Steps
        remediations.append(
            RemediationAction(
                priority=1,
                action_type="BLOCK_IP",
                title=f"Block Source IP {src_ip}",
                details=f"Apply perimeter firewall rule: iptables -A INPUT -s {src_ip} -j DROP",
            )
        )

        if severity in ["HIGH", "CRITICAL"]:
            remediations.append(
                RemediationAction(
                    priority=2,
                    action_type="ISOLATE_HOST",
                    title=f"Isolate Target Host {dst_ip}",
                    details=f"Temporarily restrict inbound traffic to internal host {dst_ip} pending malware sweep.",
                )
            )

        remediations.append(
            RemediationAction(
                priority=3,
                action_type="CAPTURE_PCAP",
                title="Initiate Full Packet Trace",
                details=f"Trigger agent packet trace on interface matching flow {src_ip} -> {dst_ip}.",
            )
        )

        return mitre_mappings, remediations
