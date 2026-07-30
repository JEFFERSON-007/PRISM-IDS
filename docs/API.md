# API & WebSocket Specification

## REST API Endpoints (`/api/v1`)

### 1. Health Diagnostics
- `GET /api/v1/health`: Full health check returning database status, uptime, latency, and system environment info.
- `GET /api/v1/health/readiness`: Kubernetes readiness probe returning 200 OK when database connection is healthy.
- `GET /api/v1/health/liveness`: Kubernetes liveness probe returning process uptime.

### 2. System Status
- `GET /api/v1/status`: Overview of active WebSocket connections, database connection status, and load.

### 3. Authentication Infrastructure
- `POST /api/v1/auth/token`: Issue test JWT Access and Refresh token pair for a target role.
- `GET /api/v1/auth/me`: Validate Bearer token and inspect decoded claims (`TokenData`).
- `GET /api/v1/auth/admin-check`: Role-restricted endpoint checking `Role.ADMIN` permission.

---

## WebSocket Infrastructure (`/ws/v1/connect`)

Connect via WebSocket client: `ws://localhost:8000/ws/v1/connect`

### Message Formats

#### Client Ping
```json
{
  "type": "ping",
  "timestamp": 1722350000
}
```
*Server Response*:
```json
{
  "type": "pong",
  "timestamp": 1722350000
}
```

#### Channel Subscription
```json
{
  "type": "subscribe",
  "channel": "security_alerts"
}
```
*Server Response*:
```json
{
  "type": "subscribed",
  "channel": "security_alerts"
}
```
