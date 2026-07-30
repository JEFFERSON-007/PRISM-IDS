"""Unit tests for Dashboard schemas."""

from datetime import datetime, timezone
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    SeverityCountSummary,
)


def test_dashboard_summary_schema() -> None:
    """Test DashboardSummaryResponse schema."""
    summary = DashboardSummaryResponse(
        timestamp=datetime.now(timezone.utc),
        alert_counts=SeverityCountSummary(critical=2, high=5, medium=10, low=20, informational=50, total=87),
        open_incidents_count=3,
        average_risk_score=68.5,
        active_agents_count=4,
        total_agents_count=5,
        top_target_hosts=[],
        top_attacker_ips=[],
        top_triggered_rules=[],
    )

    assert summary.open_incidents_count == 3
    assert summary.alert_counts.critical == 2
    assert summary.average_risk_score == 68.5
