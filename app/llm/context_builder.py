"""Context Builder for LLM Prompt Construction."""

from typing import Any, Dict, Optional
from app.models.alert import Alert


class ContextBuilder:
    """Builds sanitized, structured JSON telemetry context for LLM prompts."""

    @staticmethod
    def build_alert_context(alert_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize raw alert data into clean prompt context."""
        return {
            "alert_id": alert_dict.get("alert_id", "UNKNOWN"),
            "timestamp": str(alert_dict.get("timestamp", "")),
            "severity": alert_dict.get("severity", "MEDIUM"),
            "risk_score": alert_dict.get("risk_score", 50.0),
            "detection_method": alert_dict.get("detection_method", "HYBRID"),
            "confidence": alert_dict.get("confidence", 0.5),
            "network_flow": {
                "source_ip": alert_dict.get("src_ip", "0.0.0.0"),
                "source_port": alert_dict.get("src_port", 0),
                "destination_ip": alert_dict.get("dst_ip", "0.0.0.0"),
                "destination_port": alert_dict.get("dst_port", 0),
                "protocol": alert_dict.get("protocol", "TCP"),
            },
            "triggered_signature_rules": alert_dict.get("matched_rules", []),
            "ml_model_prediction": alert_dict.get("ml_prediction", {}),
            "evidence_features": alert_dict.get("evidence_summary", {}),
            "occurrence_count": alert_dict.get("occurrence_count", 1),
            "correlation_id": alert_dict.get("correlation_id", "None"),
        }

    @staticmethod
    def build_alert_context_from_orm(alert: Alert) -> Dict[str, Any]:
        """Convert Alert ORM model into prompt context."""
        return ContextBuilder.build_alert_context({
            "alert_id": alert.alert_id,
            "timestamp": alert.timestamp.isoformat(),
            "severity": alert.severity,
            "risk_score": alert.risk_score,
            "detection_method": alert.detection_method,
            "confidence": alert.confidence,
            "src_ip": alert.src_ip,
            "src_port": alert.src_port,
            "dst_ip": alert.dst_ip,
            "dst_port": alert.dst_port,
            "protocol": alert.protocol,
            "matched_rules": alert.matched_rules,
            "ml_prediction": alert.ml_prediction,
            "evidence_summary": alert.evidence_summary,
            "occurrence_count": alert.occurrence_count,
            "correlation_id": alert.correlation_id,
        })
