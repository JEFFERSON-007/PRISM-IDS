# PRISM Agent Architecture & Lifecycle

## Daemon Lifecycle Architecture

```
┌────────────────────────────────────────────────────────────┐
│              Agent Lifecycle Orchestrator                 │
│               (agent/services/lifecycle.py)               │
└─────────────────────────────┬──────────────────────────────┘
                              │
  ┌───────────────────────────┼───────────────────────────┐
  │                           │                           │
  ▼                           ▼                           ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Credentials Store│  │ System Collector │  │ AgentHTTPClient  │
│ (load/save key)  │  │ (collect metrics)│  │ (REST / API v1)  │
└──────────────────┘  └──────────────────┘  └────────┬─────────┘
                                                     │
                                 ┌───────────────────┴───────────┐
                                 │                               │
                                 ▼                               ▼
                       ┌──────────────────┐            ┌──────────────────┐
                       │ Heartbeat Service│            │ WebSocket Client │
                       │ (every N seconds)│            │ (ws://.../connect)│
                       └──────────────────┘            └──────────────────┘
```

---

## Startup Sequence

1. **Initialize Logging**: Set up structured logging handlers.
2. **Load Configuration**: Read parameters from environment variables / `.env.agent`.
3. **Verify Local Credentials**: Check for `.agent_credentials.json`.
4. **Onboard / Register**: If no credentials exist, execute `POST /api/v1/agents/register` with static hardware info and store returned `agent_id` and `secret_key`.
5. **Start Heartbeat Service**: Launch background telemetry task submitting health metrics every `HEARTBEAT_INTERVAL` seconds.
6. **Establish WebSocket Connection**: Connect to server `/ws/v1/connect` with auto-reconnect loop.
