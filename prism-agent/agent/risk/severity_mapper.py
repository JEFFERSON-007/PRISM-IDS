"""Severity Level Classification Mapper."""

from agent.core.config import agent_settings
from agent.detection.detection_models import SeverityEnum


class SeverityMapper:
    """Maps numerical Risk Score (0-100) to SeverityEnum based on configuration thresholds."""

    @classmethod
    def map_severity(cls, risk_score: float) -> SeverityEnum:
        """Map risk score to SeverityEnum."""
        if risk_score >= agent_settings.RISK_THRESHOLD_CRITICAL:
            return SeverityEnum.CRITICAL
        if risk_score >= agent_settings.RISK_THRESHOLD_HIGH:
            return SeverityEnum.HIGH
        if risk_score >= agent_settings.RISK_THRESHOLD_MEDIUM:
            return SeverityEnum.MEDIUM
        if risk_score >= agent_settings.RISK_THRESHOLD_LOW:
            return SeverityEnum.LOW
        return SeverityEnum.LOW
