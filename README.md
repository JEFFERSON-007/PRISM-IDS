<div align="center">

# 🛡️ PRISM IDS
### **Predictive Reasoning & Intelligent Security Monitoring**

[![CI/CD Pipeline](https://github.com/JEFFERSON-007/PRISM-IDS/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/JEFFERSON-007/PRISM-IDS/actions)
[![Python Version](https://img.shields.io/badge/Python-3.12%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Ollama](https://img.shields.io/badge/Ollama-Qwen2.5%3A3B-black.svg?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com/)
[![Docker](https://img.shields.io/badge/Docker-Production%20Ready-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<br/>

*An Enterprise-Grade, Real-Time Intrusion Detection System & Security Operations Center (SOC) Platform powered by Hybrid Signature + ML Detection Engines, Scapy Network Sensors, and Local Ollama AI Security Analyst (`qwen2.5:3b`).*

[Architecture](#-system-architecture) • [Features](#-key-features) • [Deployment & Launch](#-getting-started--deployment) • [Remote Monitoring](#-monitoring-remote-devices-multi-agent) • [AI Analyst](#-ai-security-analyst-ollama) • [Troubleshooting](#-troubleshooting--faq) • [Documentation](#-documentation-suite)

</div>

---

## 👁️ System Overview

**PRISM IDS** is an end-to-end cyber threat detection platform engineered for modern enterprise environments. It combines high-throughput raw packet capture, 5-tuple flow generation, statistical feature extraction, dual signature & Random Forest Machine Learning detection, risk score normalization, and automated threat deduplication into a unified security monitoring platform.

### 🌟 Key Highlights
- **⚡ High-Performance Sensor Pipeline**: Multithreaded Scapy packet capture daemon with BPF filtering, async bounded queues, and zero packet drop under heavy load.
- **🧠 Hybrid Detection Fusion**: Combines deterministic signature matching (`rules/signature_rules.json`) with an offline-trained Scikit-learn Random Forest model.
- **📊 Real-Time Obsidian SOC Dashboard**: A React 19 + TypeScript + Vite dashboard featuring glassmorphic UI cards, live WebSocket alert streaming, and Recharts threat analytics.
- **🌐 Centralized Multi-Agent Monitoring**: Deploy lightweight sensor agents onto any number of remote machines (Windows, Linux, Cloud VMs) pointing back to your Central Server.
- **🤖 Local Ollama AI Analyst (`qwen2.5:3b`)**: Local LLM assistant that explains attack telemetry, maps threats to MITRE ATT&CK framework (`T1046`, `T1110`, `T1190`, `T1498`), and suggests prioritized mitigations without sending data off-site.
- **📄 Automated PDF Incident Briefings**: One-click generation of branded, audit-ready security reports.

---

## 🏗️ System Architecture

```
                  +-------------------------------------------------------------+
                  |         PRISM IDS Sensor Fleet (Python 3.12 / Scapy)        |
                  +------------------------------+------------------------------+
                                                 |
                                     (Raw Packet Acquisition)
                                                 v
                                  (5-Tuple Flow Engine O(1))
                                                 v
                                (Feature Vector Extraction)
                                                 v
                              (Hybrid Signature + ML Classifier)
                                                 v
                                 (Risk Score Normalizer 0-100)
                                                 |
                                        (HTTP POST / Alerts)
                                                 v
+---------------------------------------------------------------------------------------------------+
|                                  PRISM FastAPI Core Backend                                       |
|                                                                                                   |
|   +--------------------------+   +-----------------------------+   +---------------------------+  |
|   | PostgreSQL 16 DB         |   | WebSocket Streaming Engine  |   | AI Analyst (Ollama LLM)   |  |
|   | (Async SQLAlchemy 2.0)   |   | (ws://localhost:8000/ws)    |   | (qwen2.5:3b Cache Engine) |  |
|   +--------------------------+   +-----------------------------+   +---------------------------+  |
+------------------------------------------------+--------------------------------------------------+
                                                 |
                                     (REST & SSE Data Streams)
                                                 v
                  +------------------------------+------------------------------+
                  |      PRISM React 19 SOC Dashboard (Vite / Tailwind CSS)     |
                  +-------------------------------------------------------------+
```

---

## 🔥 Key Features

### 1. Network Telemetry & Packet Engine
- **BPF Capture Filtering**: Real-time packet acquisition using Scapy with raw socket listener threads.
- **Canonical 5-Tuple Flow Tracker**: Tracks `(src_ip, dst_ip, src_port, dst_port, protocol)` bi-directionally with active/idle expiration sweeps.
- **Entropy & Statistical Metrics**: Computes packet length variance, TCP flag ratios, and Shannon Entropy ($H(X)$) across flow payloads.

### 2. Hybrid Threat Detection & Risk Engine
- **Signature Engine**: Evaluates configurable JSON rules (`signature_rules.json`) matching pattern strings, header constraints, and protocol anomalies.
- **Scikit-Learn ML Model**: Evaluates extracted 24-feature vectors using a Random Forest classifier.
- **Confidence Fusion**: Merges signature and ML detection outputs into normalized Risk Scores ($0-100$).
- **Alert Deduplication**: Deduplicates repeating alerts within a sliding time-window to prevent SOC alert fatigue.

### 3. AI Security Analyst (Ollama `qwen2.5:3b`)
- **Strict SOC L3 System Prompt**: Operates with explicit instructions never to classify traffic, focusing solely on explanation and recommendation.
- **MITRE ATT&CK Mapping**: Maps detected threat behaviors to standardized MITRE tactics and techniques.
- **Response Caching**: `LLMCache` eliminates duplicate LLM calls for recurring alert patterns.
- **SSE Streaming Chat**: Real-time token streaming interface (`POST /api/ai/chat?stream=true`).

---

## ⚡ Getting Started & Deployment

### System Prerequisites
- **Git**: [git-scm.com](https://git-scm.com/)
- **Python**: 3.12 or newer ([python.org](https://www.python.org/))
- **Node.js**: 18.0 or newer ([nodejs.org](https://nodejs.org/))
- **Docker Desktop**: Recommended for containerized deployment ([docker.com](https://www.docker.com/))
- **Ollama**: Recommended for local LLM briefings ([ollama.com](https://ollama.com/))

---

### 🐳 Method 1: Containerized Run (Docker Compose - Recommended for Any OS)

This method runs PostgreSQL 16, FastAPI Backend, React SOC Dashboard, and Scapy Agent in Docker containers with a single command.

#### 1. Start Docker Engine
- **Windows / macOS**: Open **Docker Desktop** application from your menu and wait until the status indicator turns **Green ("Engine Running")**.
- **Linux**: Ensure Docker daemon is running (`sudo systemctl start docker`).

#### 2. Launch Stack
```bash
# Clone the repository
git clone https://github.com/JEFFERSON-007/PRISM-IDS.git
cd PRISM-IDS

# (Optional) Pull Ollama AI model locally
ollama pull qwen2.5:3b

# Launch all microservices
docker-compose up --build -d
```

#### 3. Access Services
| Service | URL | Description |
| :--- | :--- | :--- |
| **SOC Dashboard** | `http://localhost` | React 19 Frontend Dashboard |
| **FastAPI Backend** | `http://localhost:8000` | REST API Server Core |
| **Swagger API Docs** | `http://localhost:8000/docs` | Interactive OpenAPI Documentation |
| **AI Analyst Health** | `http://localhost:8000/api/ai/health` | Ollama LLM Connection Status |
| **WebSocket Stream** | `ws://localhost:8000/ws/v1/connect` | Live Event Streaming Endpoint |

---

### 💻 Method 2: Native Standalone Run (Local Terminal Windows)

If you prefer to run services directly on your host machine without Docker containers:

#### 1. Start Database (PostgreSQL 16)
- **Option A (Docker database only)**: `docker-compose up -d postgres`
- **Option B (Windows Native PostgreSQL)**: Ensure `postgresql-x64-16` service is running in Windows Services.

#### 2. Start FastAPI Backend Server (Terminal 1)
```bash
# Navigate to project root
cd PRISM-IDS

# Install server dependencies
python -m pip install -r requirements.txt

# Start backend server
python -m uvicorn app.main:app --reload --port 8000
```

#### 3. Start React SOC Dashboard (Terminal 2)
```bash
# Navigate to dashboard directory
cd PRISM-IDS/prism-dashboard

# Install frontend node packages
npm.cmd install   # On Windows (or 'npm install' on Linux/macOS)

# Launch Vite development server
npm.cmd run dev   # On Windows (or 'npm run dev' on Linux/macOS)
```
*Open **http://localhost:5173** in your browser.*

#### 4. Start IDS Agent Network Sensor (Terminal 3)
```bash
# Navigate to agent directory
cd PRISM-IDS/prism-agent

# Install agent dependencies
python -m pip install -r requirements.txt

# Run the agent daemon
python -m agent.main
```

---

## 📡 Monitoring Remote Devices (Multi-Agent Setup)

You can deploy the `prism-agent` sensor to any number of remote computers, cloud servers, or Linux VMs to monitor all devices centrally on your Master SOC Dashboard!

```
                               Central SOC Dashboard
                                         │
                                         ▼
                            Central PRISM FastAPI Server
                             (http://192.168.1.50:8000)
                                         ▲
           ┌─────────────────────────────┼─────────────────────────────┐
           │                             │                             │
    Remote Agent 1                Remote Agent 2                Remote Agent 3
(Windows Laptop / Office)     (Linux Web Gateway / Cloud)    (Database Server / Local)
```

### Remote Agent Deployment Steps:

1. **Find Central Server IP**:
   Find the IP address of the machine running your Central PRISM Server (`ipconfig` on Windows or `ifconfig` on Linux, e.g. `192.168.1.50`).

2. **Copy Agent to Target Machine**:
   Copy or clone the `prism-agent/` directory to the remote machine you wish to monitor.

3. **Configure Central Server URL**:
   On the remote machine, open `prism-agent/.env.agent` and point `SERVER_URL` to your Central Server:
   ```env
   AGENT_NAME="remote-server-gateway"
   SERVER_URL="http://192.168.1.50:8000"
   ```

4. **Start Remote Agent Sensor**:
   On the remote machine, run:
   ```bash
   cd prism-agent
   python -m pip install -r requirements.txt
   python -m agent.main
   ```

*The remote agent will automatically register with your Central Server, stream telemetry, and push live threat alerts to your Central SOC Dashboard!*

---

## 🤖 AI Security Analyst (Ollama)

The PRISM AI Analyst endpoints expose local LLM capabilities via `/api/ai/*`:

### Endpoints Overview

#### 1. AI Health Check
```http
GET /api/ai/health
```
**Response:**
```json
{
  "online": true,
  "model_name": "qwen2.5:3b",
  "model_available": true,
  "loaded": true,
  "available_models": ["qwen2.5:3b"]
}
```

#### 2. Alert Explanation & MITRE Mapping
```http
POST /api/ai/alert/{alert_id}/summary
```
**Response:**
```json
{
  "alert_id": "ALT-2026-8842",
  "executive_summary": "High-severity SYN Flood Denial of Service attack targeting Web Gateway.",
  "technical_explanation": "Source host 192.168.1.100 initiated 4,500 SYN packets per second without completing TCP handshakes.",
  "trigger_rationale": "High Risk Score (92.5/100) triggered by SYN ratio exceeding 0.95 and high entropy payload.",
  "risk_assessment": "CRITICAL. Immediate risk of web gateway exhaustion and legitimate client connection drops.",
  "mitre_attack_mapping": [
    {
      "tactic": "Impact",
      "technique_id": "T1498",
      "technique_name": "Network Denial of Service",
      "description": "Adversaries may perform Network DoS attacks to degrade or disrupt availability."
    }
  ],
  "remediation_actions": [
    {
      "priority": 1,
      "action_type": "BLOCK_IP",
      "title": "Enforce Perimeter Firewall Drop Rule",
      "details": "iptables -A INPUT -s 192.168.1.100 -j DROP"
    }
  ],
  "investigation_steps": [
    "Verify whether source IP 192.168.1.100 belongs to an internal compromised host.",
    "Inspect upstream router netflow logs for spoofing indicators."
  ],
  "cached": false
}
```

#### 3. Interactive Analyst Chat (SSE Streaming)
```http
POST /api/ai/chat
Content-Type: application/json

{
  "prompt": "How should I mitigate this SYN Flood alert?",
  "alert_id": "ALT-2026-8842",
  "stream": false
}
```

#### 4. Executive Security Report
```http
POST /api/ai/report
Content-Type: application/json

{
  "timeframe": "24h",
  "top_limit": 5
}
```

---

## 🔧 Troubleshooting & FAQ

| Issue / Error | Root Cause | Solution |
| :--- | :--- | :--- |
| **`failed to connect to docker API... daemon not running`** | Docker Desktop application is closed. | Launch **Docker Desktop** from Windows Start Menu and wait until engine status turns green. |
| **`Connect call failed ('127.0.0.1', 5432)`** | PostgreSQL database service is stopped. | Run `docker-compose up -d postgres` or start `postgresql-x64-16` in Windows Services. |
| **`'vite' is not recognized as an internal command`** | Node packages not installed in `prism-dashboard`. | Run `npm.cmd install` (or `npm install`) inside `prism-dashboard` folder first. |
| **`Select an app to open 'npm'` popup** | Windows file association for `.cmd` files. | Use `npm.cmd run dev` or `npx vite` in Windows Command Prompt/PowerShell. |
| **`ModuleNotFoundError: No module named 'agent'`** | Python current directory import path issue. | Run `python -m agent.main` from inside the `prism-agent` directory. |
| **`ollama: command not found`** | Ollama binary not installed on host. | Install from [ollama.com](https://ollama.com/). *Note: PRISM IDS automatically falls back to internal rules if Ollama is absent.* |

---

## 🛠️ Technology Stack

```
================================================================================================
LAYER               TECHNOLOGIES UTILIZED
================================================================================================
Sensor Agent        Python 3.12+, Scapy, Pydantic v2, HTTPX, Scikit-Learn, Joblib, Structlog
Backend Core        FastAPI, Async SQLAlchemy 2.0, PostgreSQL 16, Asyncpg, Alembic, PyJWT, Passlib
Frontend SOC        React 19, TypeScript 5, Vite, Tailwind CSS, Recharts, Zustand, Sonner, Axios
AI Analyst          Ollama API Runtime, Qwen2.5:3b Model, HTTPX Async, In-Memory LLMCache
DevOps & CI/CD      Docker, Docker Compose, NGINX, GitHub Actions CI/CD Pipeline, Pytest
================================================================================================
```

---

## 🧪 Running Unit & Integration Tests

```bash
# Run Server Unit Tests
PYTHONPATH=. pytest tests/unit/

# Run Agent Sensor Tests
cd prism-agent
PYTHONPATH=. pytest tests/

# Run Full End-to-End Pipeline Integration Test
PYTHONPATH=. pytest tests/integration/test_e2e_pipeline.py
```

---

## 📖 Documentation Suite

Comprehensive technical documentation is maintained in the [`docs/`](docs) folder:

- 📘 **[Architecture Guide](docs/ArchitectureGuide.md)**: Deep dive into 5-tuple tracking, feature extraction formulas, and system data flows.
- 📙 **[Deployment Guide](docs/DeploymentGuide.md)**: Hardened production setup using NGINX, TLS, PostgreSQL tuning, and systemd daemons.
- 📗 **[Developer Guide](docs/DeveloperGuide.md)**: Coding standards, Clean Architecture rules, and repository patterns.
- 📕 **[Installation Guide](docs/InstallationGuide.md)**: Bare-metal and containerized step-by-step deployment instructions.
- 📓 **[Operations Manual](docs/OperationsManual.md)**: Incident response runbooks, backup procedures, and monitoring alerts.
- 🛡️ **[Security Guide](docs/SecurityGuide.md)**: RBAC permission matrices, rate limiting thresholds, and secret storage rules.
- 📋 **[Threat Model](docs/ThreatModel.md)**: STRIDE threat modeling analysis and risk mitigations.

---

## 📜 License

PRISM IDS is licensed under the **[MIT License](LICENSE)**.

<div align="center">
  <sub>Developed with ❤️ by the PRISM IDS Security Engineering Team.</sub>
</div>
