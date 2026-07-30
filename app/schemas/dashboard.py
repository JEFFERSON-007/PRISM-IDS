"""Pydantic Schemas for Dashboard Executive Summary and Real-Time Analytics."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class SeverityCountSummary(BaseModel):
    """Alert counts grouped by severity."""

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    informational: int = 0
    total: int = 0


class TopTargetHost(BaseModel):
    """Top targeted destination IP address."""

    dst_ip: str
    alert_count: int
    highest_severity: str


class TopAttackerIP(BaseModel):
    """Top attacking source IP address."""

    src_ip: str
    alert_count: int
    highest_severity: str


class TopRuleMatch(BaseModel):
    """Top triggered signature rule."""

    rule_name: str
    trigger_count: int


class DashboardSummaryResponse(BaseModel):
    """SOC Executive Dashboard Summary."""

    timestamp: datetime
    alert_counts: SeverityCountSummary
    open_incidents_count: int
    average_risk_score: float
    active_agents_count: int
    total_agents_count: int
    top_target_hosts: List[TopTargetHost]
    top_attacker_ips: List[TopAttackerIP]
    top_triggered_rules: List[TopRuleMatch]


class ProtocolDistributionItem(BaseModel):
    """Protocol volume distribution."""

    protocol: str
    count: int
    percentage: float


class NetworkAnalyticsResponse(BaseModel):
    """Network Analytics & Traffic Profile."""

    timestamp: datetime
    protocol_distribution: List[ProtocolDistributionItem]
    top_destination_ports: List[Dict[str, Any]]
    top_source_ips: List[Dict[str, Any]]
    traffic_volume_summary: Dict[str, Any]


class SystemHealthResponse(BaseModel):
    """PRISM Server System & WebSocket Health."""

    timestamp: datetime
    server_status: str
    database_status: str
    websocket_connections_count: int
    registered_agents_count: int
    online_agents_count: int
    offline_agents_count: int
    cpu_percent: float
    memory_percent: float
    uptime_seconds: float
