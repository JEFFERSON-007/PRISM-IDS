"""End-to-End Integration Test for PRISM IDS Full Detection & Reporting Pipeline."""

from datetime import datetime, timezone
import pytest

from app.domain.mitre import MitreAttackCatalog
from app.llm.context_builder import ContextBuilder
from app.llm.recommendation_engine import RecommendationEngine
from app.schemas.alert import AlertCreate
from app.utils.pdf_generator import IncidentReportGenerator


def test_full_end_to_end_pipeline() -> None:
    """Validate full pipeline flow from packet DTO through alert ingestion, MITRE mapping, LLM context, and report PDF generation."""
    now = datetime.now(timezone.utc)

    # 1. Alert Ingestion DTO
    alert_in = AlertCreate(
        alert_id="ALT-E2E-999",
        timestamp=now,
        detection_id="DET-E2E-001",
        flow_id="FLOW-E2E-100",
        src_ip="192.168.1.100",
        dst_ip="10.0.0.1",
        src_port=54321,
        dst_port=80,
        protocol="TCP",
        risk_score=94.5,
        severity="CRITICAL",
        detection_method="HYBRID",
        confidence=0.96,
        matched_rules=[{"rule_id": "SIG-002", "name": "TCP SYN Flood", "severity": "CRITICAL"}],
    )
    assert alert_in.alert_id == "ALT-E2E-999"

    # 2. MITRE ATT&CK Mapping
    mitre_mappings = MitreAttackCatalog.map_alert_telemetry(
        dst_port=alert_in.dst_port, protocol=alert_in.protocol, severity=alert_in.severity
    )
    assert len(mitre_mappings) > 0
    assert mitre_mappings[0]["technique_id"] == "T1046"

    # 3. Context Builder & LLM Recommendation Engine
    ctx = ContextBuilder.build_alert_context(alert_in.model_dump(mode="json"))
    mitre_recs, remediations = RecommendationEngine.generate_recommendations(ctx)
    assert len(remediations) >= 2
    assert remediations[0].action_type == "BLOCK_IP"

    # 4. Incident Security Report HTML Generation
    incident_data = {
        "incident_id": "INC-E2E-2026-0001",
        "title": "E2E Critical SYN Flood Threat Campaign",
        "severity": alert_in.severity,
        "status": "OPEN",
        "description": f"Automated E2E test detected high risk threat from {alert_in.src_ip}.",
    }
    html_report = IncidentReportGenerator.generate_html_report(incident_data)
    assert "PRISM" in html_report
    assert "INC-E2E-2026-0001" in html_report
