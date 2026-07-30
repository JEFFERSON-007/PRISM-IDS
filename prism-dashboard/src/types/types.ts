export type Severity = 'INFORMATIONAL' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type DetectionMethod = 'SIGNATURE' | 'MACHINE_LEARNING' | 'HYBRID';
export type AlertStatus = 'OPEN' | 'ACKNOWLEDGED' | 'RESOLVED';
export type IncidentStatus = 'OPEN' | 'ACKNOWLEDGED' | 'RESOLVED' | 'REOPENED';

export interface RuleMatch {
  rule_id: str;
  name: string;
  severity: Severity;
  evidence?: Record<string, any>;
}

export interface MLPrediction {
  is_malicious: boolean;
  probability: number;
  model_name: string;
  confidence: number;
}

export interface Alert {
  id: string;
  alert_id: string;
  timestamp: string;
  first_seen: string;
  last_seen: string;
  detection_id: string;
  agent_id?: string;
  flow_id: string;
  src_ip: string;
  dst_ip: string;
  src_port: number;
  dst_port: number;
  protocol: string;
  risk_score: number;
  severity: Severity;
  detection_method: DetectionMethod;
  matched_rules?: RuleMatch[];
  ml_prediction?: MLPrediction;
  confidence: number;
  evidence_summary?: Record<string, any>;
  status: AlertStatus;
  occurrence_count: number;
  correlation_id?: string;
}

export interface AlertPaginationResponse {
  items: Alert[];
  page: number;
  page_size: number;
  total_records: number;
  total_pages: number;
}

export interface IncidentNote {
  author: string;
  timestamp: string;
  note: string;
}

export interface Incident {
  id: string;
  incident_id: string;
  title: string;
  description?: string;
  severity: Severity;
  status: IncidentStatus;
  assigned_to_user_id?: string;
  created_at: string;
  updated_at: string;
  notes?: IncidentNote[];
  correlation_id?: string;
}

export interface IncidentPaginationResponse {
  items: Incident[];
  page: number;
  page_size: number;
  total_records: number;
  total_pages: number;
}

export interface SeverityCountSummary {
  critical: number;
  high: number;
  medium: number;
  low: number;
  informational: number;
  total: number;
}

export interface TopTargetHost {
  dst_ip: string;
  alert_count: number;
  highest_severity: string;
}

export interface TopAttackerIP {
  src_ip: string;
  alert_count: number;
  highest_severity: string;
}

export interface TopRuleMatch {
  rule_name: string;
  trigger_count: number;
}

export interface DashboardSummary {
  timestamp: string;
  alert_counts: SeverityCountSummary;
  open_incidents_count: number;
  average_risk_score: number;
  active_agents_count: number;
  total_agents_count: number;
  top_target_hosts: TopTargetHost[];
  top_attacker_ips: TopAttackerIP[];
  top_triggered_rules: TopRuleMatch[];
}

export interface AgentNode {
  id: string;
  agent_id: string;
  name: string;
  hostname: string;
  ip_address: string;
  os_type: string;
  version: string;
  is_online: boolean;
  health_status: 'healthy' | 'degraded' | 'unhealthy';
  last_heartbeat: string;
}

export interface SystemHealth {
  timestamp: string;
  server_status: string;
  database_status: string;
  websocket_connections_count: number;
  registered_agents_count: number;
  online_agents_count: number;
  offline_agents_count: number;
  cpu_percent: number;
  memory_percent: number;
  uptime_seconds: number;
}

export interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
}
