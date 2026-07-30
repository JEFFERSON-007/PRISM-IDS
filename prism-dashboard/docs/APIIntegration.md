# API Integration Specification

The React dashboard connects to the PRISM FastAPI server via Axios HTTP REST calls and WebSocket streaming.

## REST Endpoints Consumed
- `POST /api/v1/auth/login`: Form-encoded JWT token retrieval.
- `GET /api/v1/alerts`: Paginated search & multi-filter query.
- `GET /api/v1/incidents`: Incident list & status management.
- `GET /api/v1/dashboard/summary`: Executive SOC metrics.
- `GET /api/v1/dashboard/network`: Traffic & protocol analytics.
- `GET /api/v1/dashboard/system`: Infrastructure & server health.

## WebSocket Streaming
- URL: `ws://localhost:8000/ws/v1/connect?token=<jwt>`
- Events: `NEW_ALERT`, `INCIDENT_UPDATE`.
