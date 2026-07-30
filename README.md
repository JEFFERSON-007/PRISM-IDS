# PRISM IDS (Predictive Reasoning & Intelligent Security Monitoring)

[![CI/CD Pipeline](https://github.com/prism-ids/prism-ids/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/prism-ids/prism-ids/actions)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-emerald.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-cyan.svg)](https://react.dev/)
[![Ollama](https://img.shields.io/badge/Ollama-Qwen2.5%3A3B-purple.svg)](https://ollama.com/)
[![Docker](https://img.shields.io/badge/Docker-Production%20Ready-blue.svg)](https://www.docker.com/)

**PRISM IDS** is an enterprise-grade, real-time Intrusion Detection Platform built with Clean Architecture, a high-performance Python Scapy agent pipeline, FastAPI backend services, a sleek obsidian dark-themed React 19 SOC Dashboard, MITRE ATT&CK mapping, and local Ollama LLM integration (`qwen2.5:3b`) for AI-assisted security briefings.

---

## Architecture Overview

```
                      +------------------------------------------+
                      |    PRISM IDS Agent Fleet (Scapy/Python)  |
                      +--------------------+---------------------+
                                           |
                                 (Packet Capture)
                                           v
                              (Flow Generation 5-Tuple)
                                           v
                             (Feature Extraction Vector)
                                           v
                            (Hybrid Signature + ML Engine)
                                           v
                              (Risk Engine & Deduplication)
                                           |
                                  (HTTP POST / Alerts)
                                           v
+-----------------------------------------------------------------------------------+
|                            PRISM FastAPI Server Core                              |
|                                                                                   |
|  +--------------------+  +----------------------+  +---------------------------+  |
|  | PostgreSQL DB      |  | WebSocket Broadcast  |  | AI Security Analyst (LLM) |  |
|  | (Alerts/Incidents) |  | (ws://.../connect)   |  | (Ollama / qwen2.5:3b)     |  |
|  +--------------------+  +----------------------+  +---------------------------+  |
+------------------------------------------+----------------------------------------+
                                           |
                                (REST & WebSocket Streams)
                                           v
                      +--------------------+---------------------+
                      |    PRISM React SOC Dashboard (Vite)      |
                      +------------------------------------------+
```

---

## Features

- **Real-Time Packet Capture Engine**: Multithreaded Scapy packet ingestion thread daemon with BPF filtering, async bounded queues, and zero packet loss.
- **Flow Generation Engine**: Bi-directional 5-tuple canonical flow tracking with idle/active time window sweeping ($O(1)$ hash table).
- **Advanced Feature Extraction**: Statistical timing metrics, TCP flag ratios, Shannon entropy calculation ($H(X)$), and application service classifiers.
- **Hybrid Intrusion Detection Engine**: Dual signature rule engine (`rules/signature_rules.json`) + Scikit-learn Random Forest ML model classifier with confidence fusion.
- **Risk Engine & Alert Management**: Normalized Risk Score calculation ($0-100$), sliding time-window deduplication, and campaign correlation.
- **FastAPI Server Foundation**: Async SQLAlchemy 2.0 PostgreSQL ORM, Alembic database migrations, JWT authentication, and token-bucket rate limiting.
- **Local Ollama AI Security Analyst (`qwen2.5:3b`)**:
  - `GET /api/ai/health`: Health status of Ollama service and loaded model.
  - `POST /api/ai/alert/{id}/summary`: Cached AI alert explanations & MITRE mappings.
  - `POST /api/ai/chat`: Interactive SOC Level-3 analyst Q&A (supporting SSE streaming).
  - `POST /api/ai/report`: Executive security threat reports.
- **Professional React SOC Dashboard**: Sleek obsidian dark theme (`#090d16`), live WebSocket alert toaster, Recharts threat visualizations, and incident management Kanban workflows.
- **Branded Incident PDF Reports**: Generates professional HTML/PDF Incident Security Briefings downloadable via API.
- **Production Containerization**: Multi-stage Dockerfiles and Docker Compose orchestration for all microservices.

---

## Quick Start (Docker Compose & Ollama)

```bash
# 1. Install Ollama and pull qwen2.5:3b
ollama pull qwen2.5:3b

# 2. Launch PRISM IDS microservices (PostgreSQL, Server, React Dashboard, Agent)
docker-compose up --build -d
```

- **React SOC Dashboard**: `http://localhost`
- **FastAPI Swagger API Docs**: `http://localhost:8000/docs`
- **AI Analyst Health Check**: `http://localhost:8000/api/ai/health`
- **WebSocket Endpoint**: `ws://localhost:8000/ws/v1/connect`

---

## Documentation Suite

Detailed technical guides are available in the [docs/](file:///c:/Users/mariy/OneDrive/Documents/extra%20tasks%20i%20do%20when%20i%20am%20bored/PRISM%20IDS/docs) directory:

- [Installation Guide](file:///c:/Users/mariy/OneDrive/Documents/extra%20tasks%20i%20do%20when%20i%20am%20bored/PRISM%20IDS/docs/InstallationGuide.md)
- [Deployment Guide](file:///c:/Users/mariy/OneDrive/Documents/extra%20tasks%20i%20do%20when%20i%20am%20bored/PRISM%20IDS/docs/DeploymentGuide.md)
- [Architecture Guide](file:///c:/Users/mariy/OneDrive/Documents/extra%20tasks%20i%20do%20when%20i%20am%20bored/PRISM%20IDS/docs/ArchitectureGuide.md)
- [Developer Guide](file:///c:/Users/mariy/OneDrive/Documents/extra%20tasks%20i%20do%20when%20i%20am%20bored/PRISM%20IDS/docs/DeveloperGuide.md)
- [Threat Model](file:///c:/Users/mariy/OneDrive/Documents/extra%20tasks%20i%20do%20when%20i%20am%20bored/PRISM%20IDS/docs/ThreatModel.md)
- [Security Guide](file:///c:/Users/mariy/OneDrive/Documents/extra%20tasks%20i%20do%20when%20i%20am%20bored/PRISM%20IDS/docs/SecurityGuide.md)
- [Operations Manual](file:///c:/Users/mariy/OneDrive/Documents/extra%20tasks%20i%20do%20when%20i%20am%20bored/PRISM%20IDS/docs/OperationsManual.md)

---

## License

PRISM IDS is released under the **MIT License**.
