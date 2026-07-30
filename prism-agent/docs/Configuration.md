# Agent Configuration Guide

The agent daemon is configured using environment variables or a `.env.agent` file.

| Environment Variable | Type | Default Value | Description |
|---|---|---|---|
| `SERVER_URL` | string | `http://localhost:8000` | Central PRISM Server HTTP URL |
| `WS_URL` | string | `ws://localhost:8000/ws/v1/connect` | PRISM Server WebSocket connection URL |
| `AGENT_NAME` | string | `agent-node-01` | Unique agent name |
| `AGENT_VERSION` | string | `1.0.0` | Agent daemon software version |
| `CREDENTIALS_FILE` | string | `.agent_credentials.json` | Path to store local credentials |
| `HEARTBEAT_INTERVAL` | integer | `15` | Heartbeat telemetry interval in seconds |
| `RECONNECT_INTERVAL` | integer | `5` | WebSocket reconnect delay in seconds |
| `HTTP_TIMEOUT` | float | `10.0` | HTTP request timeout in seconds |
| `LOG_LEVEL` | string | `INFO` | Log severity (DEBUG, INFO, WARNING, ERROR) |
