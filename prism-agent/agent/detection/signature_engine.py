"""Deterministic Rule-Based Signature Detection Engine."""

from typing import List, Optional
import structlog
from agent.detection.detection_models import RuleDefinition, RuleMatch
from agent.detection.rule_loader import RuleLoader
from agent.feature_extraction.feature_models import FeatureVector

logger = structlog.get_logger("prism_agent.signature_engine")


class SignatureEngine:
    """Evaluates FeatureVector against configured signature rules."""

    def __init__(self, rules: Optional[List[RuleDefinition]] = None) -> None:
        self.rules: List[RuleDefinition] = rules or RuleLoader.load_rules()

    def evaluate(self, vector: FeatureVector) -> List[RuleMatch]:
        """Evaluate FeatureVector against active signature rules."""
        matches: List[RuleMatch] = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            # Protocol Filter
            if rule.protocol != "ANY" and rule.protocol.upper() != vector.protocol.upper():
                continue

            if self._matches_rule(vector, rule):
                match = RuleMatch(
                    rule_id=rule.rule_id,
                    name=rule.name,
                    severity=rule.severity,
                    evidence={
                        "protocol": vector.protocol,
                        "duration": vector.duration,
                        "packets_per_sec": vector.packets_per_sec,
                        "total_packets": vector.total_packets,
                        "syn_ratio": vector.syn_ratio,
                    },
                )
                matches.append(match)
                logger.info(
                    "Signature Rule Match Triggered",
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    flow_id=vector.flow_id,
                    severity=rule.severity.value,
                )

        return matches

    def _matches_rule(self, vector: FeatureVector, rule: RuleDefinition) -> bool:
        """Evaluate conditions defined inside rule."""
        conds = rule.conditions

        # Port Scan Check
        if "min_packets" in conds and vector.total_packets < conds["min_packets"]:
            return False
        if "max_bytes_per_pkt" in conds and vector.avg_bytes_per_pkt > conds["max_bytes_per_pkt"]:
            return False
        if "min_packets_per_sec" in conds and vector.packets_per_sec < conds["min_packets_per_sec"]:
            return False

        # SYN Flood Check
        if "min_syn_ratio" in conds and vector.syn_ratio < conds["min_syn_ratio"]:
            return False
        if "max_ack_ratio" in conds and vector.ack_ratio > conds["max_ack_ratio"]:
            return False

        # Port check
        if "target_ports" in conds and (vector.dst_port not in conds["target_ports"]):
            return False

        return True
