"""Alert Assembly Factory Builder."""

from typing import Optional, Tuple
import structlog
from agent.core.state import agent_state
from agent.detection.detection_models import DetectionResult
from agent.risk.alert_correlation import AlertCorrelator
from agent.risk.alert_models import Alert
from agent.risk.deduplication import AlertDeduplicator

logger = structlog.get_logger("prism_agent.alert_builder")


class AlertBuilder:
    """Assembles, deduplicates, and correlates Alert objects from raw DetectionResults."""

    def __init__(self) -> None:
        self.deduplicator = AlertDeduplicator()
        self.correlator = AlertCorrelator()

    def build_alert(self, detection: DetectionResult) -> Tuple[bool, Alert]:
        """Deduplicate, set current agent_id, correlate, and return (is_new, alert)."""
        is_new, alert = self.deduplicator.process_detection(detection)

        # Inject runtime authenticated agent_id
        if agent_state.agent_id:
            alert.agent_id = agent_state.agent_id

        # Correlate alerts
        alert = self.correlator.correlate(alert)

        return is_new, alert
