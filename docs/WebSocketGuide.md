# WebSocket Real-Time Event Streaming Guide

## Connection URL

```
ws://localhost:8000/ws/v1/connect?token=<jwt_access_token>
```

## Broadcast Events

### 1. New Alert Event (`NEW_ALERT`)
Broadcasted immediately when a PRISM Agent posts a new alert:

```json
{
  "type": "NEW_ALERT",
  "alert": {
    "alert_id": "ALT-999",
    "timestamp": "2026-07-30T16:00:00Z",
    "src_ip": "192.168.1.100",
    "dst_ip": "10.0.0.1",
    "risk_score": 95.0,
    "severity": "CRITICAL"
  }
}
```

### 2. Incident Update Event (`INCIDENT_UPDATE`)
Broadcasted when an incident status, assignment, or note changes:

```json
{
  "type": "INCIDENT_UPDATE",
  "action": "STATUS_CHANGED",
  "incident": {
    "incident_id": "INC-2026-0001",
    "status": "RESOLVED"
  }
}
```
