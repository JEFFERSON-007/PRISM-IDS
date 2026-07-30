# Outbound Server Alert Transmission API

Outbound alerts are posted to PRISM Server over HTTP POST `/api/v1/alerts`:

```json
{
  "alert_id": "a9b8c7d6-e5f4-3210-9876-543210fedcba",
  "timestamp": "2026-07-30T16:00:00Z",
  "first_seen": "2026-07-30T15:59:00Z",
  "last_seen": "2026-07-30T16:00:00Z",
  "detection_id": "det-100",
  "agent_id": "agent-node-01",
  "flow_id": "flow-500",
  "src_ip": "192.168.1.100",
  "dst_ip": "10.0.0.1",
  "src_port": 54321,
  "dst_port": 22,
  "protocol": "TCP",
  "risk_score": 92.5,
  "severity": "CRITICAL",
  "detection_method": "HYBRID",
  "matched_rules": [
    {
      "rule_id": "SIG-001",
      "name": "Port Scanning Activity Detected",
      "severity": "HIGH",
      "evidence": {}
    }
  ],
  "ml_prediction": {
    "is_malicious": true,
    "probability": 0.95,
    "model_name": "RandomForestClassifier",
    "confidence": 0.95
  },
  "confidence": 0.95,
  "status": "OPEN",
  "occurrence_count": 3,
  "correlation_id": "corr-scan-192_168_1_100"
}
```
