"""Detection Fusion Engine unifying Signature and Machine Learning findings."""

from datetime import datetime, timezone
from typing import List, Optional
import structlog
from agent.detection.confidence_engine import ConfidenceEngine
from agent.detection.detection_models import (
    DetectionMethodEnum,
    DetectionResult,
    MLPredictionResult,
    RuleMatch,
    SeverityEnum,
)
from agent.feature_extraction.feature_models import FeatureVector

logger = structlog.get_logger("prism_agent.detection_fusion")


class DetectionFusion:
    """Fuses signature rule matches and ML prediction results into a DetectionResult DTO."""

    @classmethod
    def fuse(
        cls,
        vector: FeatureVector,
        matched_rules: List[RuleMatch],
        ml_result: Optional[MLPredictionResult],
    ) -> Optional[DetectionResult]:
        """Merge findings into a unified DetectionResult. Returns None if benign/no detection."""
        has_signatures = len(matched_rules) > 0
        has_ml_positive = ml_result is not None and ml_result.is_malicious

        if not has_signatures and not has_ml_positive:
            return None  # Traffic classified as benign

        # Determine Detection Method
        if has_signatures and has_ml_positive:
            method = DetectionMethodEnum.HYBRID
        elif has_signatures:
            method = DetectionMethodEnum.SIGNATURE
        else:
            method = DetectionMethodEnum.MACHINE_LEARNING

        # Compute Confidence Score
        confidence = ConfidenceEngine.calculate_confidence(matched_rules, ml_result)

        # Determine Unified Severity
        severity = SeverityEnum.LOW
        if has_signatures:
            # Take highest severity from matched rules
            rule_severities = [r.severity for r in matched_rules]
            if SeverityEnum.CRITICAL in rule_severities:
                severity = SeverityEnum.CRITICAL
            elif SeverityEnum.HIGH in rule_severities:
                severity = SeverityEnum.HIGH
            elif SeverityEnum.MEDIUM in rule_severities:
                severity = SeverityEnum.MEDIUM
        elif has_ml_positive:
            prob = ml_result.probability
            if prob >= 0.9:
                severity = SeverityEnum.HIGH
            elif prob >= 0.75:
                severity = SeverityEnum.MEDIUM
            else:
                severity = SeverityEnum.LOW

        # Elevate severity if Hybrid agreement
        if method == DetectionMethodEnum.HYBRID and severity == SeverityEnum.HIGH:
            severity = SeverityEnum.CRITICAL

        # Evidence Summary
        evidence = {
            "matched_rules_count": len(matched_rules),
            "ml_probability": ml_result.probability if ml_result else None,
            "packets_per_sec": vector.packets_per_sec,
            "total_bytes": vector.total_bytes,
            "service_name": vector.service_name,
        }

        detection = DetectionResult(
            flow_id=vector.flow_id,
            src_ip=vector.src_ip,
            dst_ip=vector.dst_ip,
            src_port=vector.src_port,
            dst_port=vector.dst_port,
            protocol=vector.protocol,
            detection_method=method,
            matched_rules=matched_rules,
            ml_prediction=ml_result,
            confidence_score=confidence,
            severity=severity,
            evidence=evidence,
        )

        logger.info(
            "Detection Result Generated",
            detection_id=detection.detection_id,
            flow_id=detection.flow_id,
            method=method.value,
            severity=severity.value,
            confidence=confidence,
        )

        return detection
