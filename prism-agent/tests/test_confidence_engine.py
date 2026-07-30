"""Unit tests for ConfidenceEngine scoring."""

from agent.detection.confidence_engine import ConfidenceEngine
from agent.detection.detection_models import MLPredictionResult, RuleMatch, SeverityEnum


def test_confidence_calculation_signature_only() -> None:
    """Test confidence score for signature match alone."""
    match = RuleMatch(rule_id="SIG-001", name="Test", severity=SeverityEnum.HIGH, evidence={})
    conf = ConfidenceEngine.calculate_confidence([match], None)
    assert conf == 0.85


def test_confidence_calculation_hybrid_boost() -> None:
    """Test elevated confidence score when both signature and ML agree."""
    match = RuleMatch(rule_id="SIG-001", name="Test", severity=SeverityEnum.HIGH, evidence={})
    ml = MLPredictionResult(is_malicious=True, probability=0.9, confidence=0.9)
    conf = ConfidenceEngine.calculate_confidence([match], ml)
    assert conf > 0.85
