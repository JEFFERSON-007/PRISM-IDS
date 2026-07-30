"""Signature Rule Loader from Configuration Files."""

import json
import os
from typing import List, Optional
import structlog
from agent.core.config import agent_settings
from agent.detection.detection_models import RuleDefinition, SeverityEnum

logger = structlog.get_logger("prism_agent.rule_loader")


class RuleLoader:
    """Loads and validates Signature Rules from disk or fallback ruleset."""

    @classmethod
    def load_rules(cls, file_path: Optional[str] = None) -> List[RuleDefinition]:
        """Load signature rules from JSON configuration file or return default rules."""
        target_path = file_path or agent_settings.RULE_FILE_PATH

        if os.path.exists(target_path):
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    rules: List[RuleDefinition] = []
                    for item in raw_data:
                        rule = RuleDefinition(**item)
                        if rule.enabled:
                            rules.append(rule)
                    logger.info("Loaded signature rules from file", count=len(rules), file_path=target_path)
                    return rules
            except Exception as exc:
                logger.error("Failed to load signature rules from file; loading defaults", error=str(exc))

        # Built-in Fallback Default Rule Set
        logger.info("Loading default built-in signature rules")
        return [
            RuleDefinition(
                rule_id="SIG-001",
                name="Port Scanning Activity Detected",
                description="High connection rate with small packet sizes",
                severity=SeverityEnum.HIGH,
                protocol="ANY",
                conditions={"min_packets": 5, "max_bytes_per_pkt": 120.0, "min_packets_per_sec": 20.0},
            ),
            RuleDefinition(
                rule_id="SIG-002",
                name="TCP SYN Flood Indicator",
                description="High SYN ratio with low ACK responses",
                severity=SeverityEnum.CRITICAL,
                protocol="TCP",
                conditions={"min_syn_ratio": 0.8, "max_ack_ratio": 0.2, "min_packets": 10},
            ),
            RuleDefinition(
                rule_id="SIG-003",
                name="ICMP Flood Attack",
                description="High ICMP packet volume rate",
                severity=SeverityEnum.HIGH,
                protocol="ICMP",
                conditions={"min_packets_per_sec": 50.0},
            ),
        ]
