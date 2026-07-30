# Agent Registration & Communication Protocol

PRISM monitoring agents securely onboard and report health telemetry to the central server.

---

## 1. Agent Onboarding / Registration

An unregistered agent sends a registration request to the server:

```http
POST /api/v1/agents/register
Content-Type: application/json

{
  "agent_name": "sensor-node-east-01",
  "hostname": "sensor01.east.prism.internal",
  "ip_address": "10.10.1.50",
  "operating_system": "Linux Ubuntu 24.04 LTS",
  "version": "1.0.0"
}
```

**Server Response (201 Created)**:
```json
{
  "agent_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "agent_name": "sensor-node-east-01",
  "secret_key": "prism_agent_a1b2c3d4e5f6...",
  "status": "registered"
}
```

> [!IMPORTANT]
> The raw `secret_key` is returned ONCE during registration. The server stores only its secure Argon2/Bcrypt hash.

---

## 2. Agent Heartbeat & Telemetry

Active agents periodically submit health telemetry using `X-Agent-ID` and `X-Agent-Secret` authentication headers:

```http
POST /api/v1/agents/heartbeat
X-Agent-ID: 9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
X-Agent-Secret: prism_agent_a1b2c3d4e5f6...
Content-Type: application/json

{
  "timestamp": "2026-07-30T21:00:00Z",
  "cpu_usage": 14.5,
  "ram_usage": 42.1,
  "disk_usage": 35.8,
  "network_status": "ok",
  "agent_version": "1.0.0"
}
```

---

## 3. Inactive Agent Timeout Detection

Agents failing to send a heartbeat for more than 90 seconds are automatically flagged as `is_online=false` and `health_status="unhealthy"`.
