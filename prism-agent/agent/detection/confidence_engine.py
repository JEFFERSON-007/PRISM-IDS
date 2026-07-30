"""Confidence Scoring Engine for Combined Signature and ML Detections."""

from typing import List, Optional
from agent.detection.detection_models import MLPredictionResult, RuleMatch, SeverityEnum


class ConfidenceEngine:
    """Calculates weighted confidence score for detections."""

    SEVERITY_WEIGHTS = {
        SeverityEnum.LOW: 0.4,
        SeverityEnum.MEDIUM: 0.6,
        SeverityEnum.HIGH: 0.85,
        SeverityEnum.CRITICAL: 1.0,
    }

    @classmethod
    def calculate_confidence(
        cls,
        matched_rules: List[RuleMatch],
        ml_result: Optional[MLPredictionResult],
    ) -> float:
        """Compute weighted confidence score between 0.0 and 1.0."""
        sig_score = 0.0
        if matched_rules:
            max_rule_weight = max(cls.SEVERITY_WEIGHTS.get(r.severity, 0.5) for r in matched_rules)
            rule_count_bonus = min(0.15, (len(matched_rules) - 1) * 0.05)
            sig_score = min(1.0, max_rule_weight + rule_count_bonus)

        ml_score = ml_result.probability if (ml_result and ml_result.is_malicious) else 0.0

        if matched_rules and ml_result and ml_result.is_malicious:
            # Hybrid agreement boosts confidence
            combined = (sig_score * 0.5) + (ml_score * 0.5) + 0.1
            return round(min(1.0, combined), 3)

        if matched_rules:
            return round(sig_score, 3)

        if ml_result and ml_result.is_malicious:
            return round(ml_score, 3)

        return 0.0
