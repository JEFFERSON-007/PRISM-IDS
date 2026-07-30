"""Risk Score Calculation Engine."""

import math
from typing import Dict
from agent.detection.detection_models import DetectionResult, SeverityEnum

SENSITIVE_PORTS: Dict[int, float] = {
    22: 15.0,    # SSH
    3389: 15.0,  # RDP
    5432: 10.0,  # Postgres DB
    3306: 10.0,  # MySQL DB
    21: 10.0,    # FTP
    80: 5.0,     # HTTP
    443: 5.0,    # HTTPS
}

SEVERITY_BASE_SCORES: Dict[SeverityEnum, float] = {
    SeverityEnum.LOW: 25.0,
    SeverityEnum.MEDIUM: 50.0,
    SeverityEnum.HIGH: 75.0,
    SeverityEnum.CRITICAL: 95.0,
}


class RiskCalculator:
    """Calculates normalized Risk Score (0 - 100) for security detection events."""

    @classmethod
    def calculate_risk(cls, detection: DetectionResult, occurrence_count: int = 1) -> float:
        """Compute normalized risk score between 0.0 and 100.0."""
        # 1. Base Score from Detection Severity
        base_score = SEVERITY_BASE_SCORES.get(detection.severity, 30.0)

        # 2. Confidence Adjustment
        confidence_factor = max(0.5, detection.confidence_score)

        # 3. Sensitive Target Port Bonus
        port_bonus = SENSITIVE_PORTS.get(detection.dst_port, 0.0)

        # 4. Raw Score
        raw_score = (base_score * confidence_factor) + port_bonus

        # 5. Multi-Occurrence Multiplier (Frequency adjustment)
        if occurrence_count > 1:
            freq_multiplier = 1.0 + (0.2 * math.log10(occurrence_count))
            raw_score *= freq_multiplier

        final_score = round(min(100.0, max(0.0, raw_score)), 1)
        return final_score
