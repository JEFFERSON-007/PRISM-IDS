"""Unit tests for Incident schemas and status updates."""

from app.schemas.incident import IncidentCreate, IncidentStatusUpdate


def test_incident_schema_validation() -> None:
    """Test IncidentCreate and IncidentStatusUpdate schemas."""
    inc_in = IncidentCreate(
        title="Unusual Port Scan Pattern",
        description="Multiple high-severity alerts detected from 192.168.1.50",
        severity="HIGH",
    )
    assert inc_in.title == "Unusual Port Scan Pattern"

    status_in = IncidentStatusUpdate(status="RESOLVED")
    assert status_in.status == "RESOLVED"
