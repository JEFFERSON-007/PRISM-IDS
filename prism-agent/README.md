# PRISM IDS Agent Daemon (Phase 3)

The **PRISM IDS Agent** is a lightweight, modular background daemon designed to run on monitored host systems. It establishes secure communications with the central PRISM Server, executes background heartbeat telemetry reporting, maintains a real-time WebSocket connection, and provides the foundation for future IDS packet capture and threat detection capabilities.

---

## Agent Features

- **Lifecycle Orchestrator**: Manages startup sequence, registration, background loops, and graceful signal shutdowns (`SIGINT`, `SIGTERM`).
- **Automatic Onboarding**: Registers with PRISM Server (`POST /api/v1/agents/register`) on initial boot and saves cryptographic credentials locally (`.agent_credentials.json`).
- **Telemetry Collector**: Measures CPU usage, RAM utilization, Disk capacity, OS information, and primary network IP address.
- **Heartbeat Daemon**: Periodically transmits system utilization metrics (`POST /api/v1/agents/heartbeat`) authenticated via `X-Agent-ID` and `X-Agent-Secret` headers.
- **Persistent WebSocket Client**: Establishes auto-reconnecting WebSocket connection to server (`/ws/v1/connect`) with ping/pong keep-alives.

---

## Quickstart

### 1. Local Python Setup

```bash
cd prism-agent
pip install -e ".[dev]"
cp .env.agent.example .env.agent
python -m agent.main
```

### 2. Run via Docker Compose

```bash
cd prism-agent/docker
docker-compose -f docker-compose.agent.yml up --build -d
```

---

## Agent Documentation

- [Agent Architecture & Lifecycle](docs/Architecture.md)
- [Configuration Reference](docs/Configuration.md)
- [Communication Protocols](docs/Communication.md)
- [Security & Credential Persistence](docs/Security.md)
- [Development & Testing Guide](docs/Development.md)
