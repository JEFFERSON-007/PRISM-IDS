"""Security Alert Correlation Engine."""

from typing import Dict, List, Optional
import structlog
from agent.risk.alert_models import Alert

logger = structlog.get_logger("prism_agent.alert_correlation")


class AlertCorrelator:
    """Correlates related alerts originating from identical source IPs or targeting common port ranges."""

    def __init__(self) -> None:
        # Key: src_ip -> List[Alert]
        self._attacker_map: Dict[str, List[Alert]] = {}

    def correlate(self, alert: Alert) -> Alert:
        """Assign correlation_id if part of an ongoing multi-target attack campaign."""
        src_ip = alert.src_ip

        if src_ip not in self._attacker_map:
            self._attacker_map[src_ip] = []

        self._attacker_map[src_ip].append(alert)
        history = self._attacker_map[src_ip]

        # Multi-target / port scan pattern detection
        if len(history) >= 3:
            dst_ports = {a.dst_port for a in history}
            dst_ips = {a.dst_ip for a in history}

            if len(dst_ports) >= 3 or len(dst_ips) >= 2:
                corr_id = f"corr-scan-{src_ip.replace('.', '_')}"
                alert.correlation_id = corr_id
                logger.info(
                    "Correlated multi-target attack campaign",
                    src_ip=src_ip,
                    correlation_id=corr_id,
                    distinct_ports=len(dst_ports),
                    distinct_ips=len(dst_ips),
                )

        return alert
