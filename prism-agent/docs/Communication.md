# Agent Communication Specifications

## REST HTTP Communication

The agent uses `httpx.AsyncClient` to send REST requests to the central server.

### Authentication Headers

All requests after registration include agent security headers:
- `X-Agent-ID`: Assigned agent UUID.
- `X-Agent-Secret`: Issued agent secret key.

### Primary Endpoints

1. `POST /api/v1/agents/register`: Initial agent onboarding.
2. `POST /api/v1/agents/heartbeat`: Periodic health telemetry delivery.
3. `GET /api/v1/agents/{id}/configuration`: Fetch current operational configuration.

---

## WebSocket Real-Time Connection

Connected to `ws://server:8000/ws/v1/connect`

- Handles automatic reconnects if connection is severed.
- Answers server ping frames with pong responses.
