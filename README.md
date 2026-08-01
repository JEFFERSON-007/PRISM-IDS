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

*An Enterprise-Grade, Real-Time Intrusion Detection System & Security Operations Center (SOC) Platform powered by Hybrid Signature + Scikit-Learn Random Forest ML Engines, Scapy Network Sensors, and Local Ollama AI Security Analyst (`qwen2.5:3b`).*

[Architecture](#-system-architecture) • [Admin Guide](#-admin-end-guide-central-soc-master) • [User Guide](#-user-end-guide-target-device-sensor) • [Deployment](#-getting-started--deployment) • [Executable (.exe)](#-standalone-windows-exe-agent-build) • [AI Analyst](#-ai-security-analyst-ollama) • [Troubleshooting](#-troubleshooting--faq)

</div>

---

## 👁️ System Overview

**PRISM IDS** is a high-performance cyber threat detection platform engineered for modern enterprise environments. It combines raw packet acquisition, canonical 5-tuple flow generation, 24-dimensional feature extraction, dual signature & Scikit-Learn Random Forest Machine Learning detection, normalized risk scoring ($0-100$), and automated threat deduplication into a unified security operations platform.

### 🌟 Key Highlights
- **⚡ High-Throughput Packet Sensor Pipeline**: Multithreaded Scapy packet capture daemon with BPF filtering, async bounded queues, and zero packet drop under heavy network load.
- **🧠 Embedded Random Forest Machine Learning Model**: Evaluates 24-dimensional network flow feature vectors (packet inter-arrival times, payload Shannon Entropy $H(X)$, TCP flag ratios) to catch zero-day anomaly attacks.
- **🛡️ Hybrid Confidence Fusion Engine**: Merges deterministic signature rules (`rules/signature_rules.json`) with ML probabilities into normalized Risk Scores ($0-100$).
- **📊 Real-Time Obsidian SOC Dashboard**: A React 19 + TypeScript + Vite dashboard featuring glassmorphic UI cards, live WebSocket alert streaming, and Recharts threat analytics.
- **🌐 Zero-Config Standalone Windows Executable Generator**: Auto-detects Central Server IP address and compiles a 34 MB self-contained `prism-agent.exe` ready to monitor any computer on your network.
- **🤖 Local Ollama AI Security Analyst (`qwen2.5:3b`)**: Local LLM assistant that explains attack telemetry, maps threats to the MITRE ATT&CK framework (`T1046`, `T1110`, `T1190`, `T1498`), and suggests prioritized mitigations without sending data off-site.

---

## 👑 ADMIN-END GUIDE (Central SOC Master)

The **Admin End** hosts the central database, central API server, Ollama AI Security Analyst, and Master SOC Dashboard.

### 1. Starting the Central Admin Server & SOC Dashboard
```bash
# Clone the repository on your Central PC
git clone https://github.com/JEFFERSON-007/PRISM-IDS.git
cd PRISM-IDS

# Launch entire platform in 1 click using Docker
docker-compose up --build -d
```
*Alternatively, start natively using `python -m uvicorn app.main:app --reload` and `npm run dev` inside `prism-dashboard`.*

### 2. Accessing the Admin Master Dashboard
- Open **http://localhost:5173** (or **`http://<YOUR_ADMIN_IP>:5173`** from any device on your network).
- **Agent Fleet Tab**: View all connected target devices in real-time alongside your primary **Admin Central HQ Server**.
- **Live Security Alerts**: View live threats streaming over WebSockets from any monitored device.
- **AI Analyst Investigation**: Click the **Blue Eye Button (👁️)** on any alert to trigger local LLM threat analysis, MITRE ATT&CK mapping (`T1498`, `T1046`), and firewall block suggestions.

---

## 👨‍💻 USER-END GUIDE (Target Device Sensor)

The **User End** is installed on any workstation, laptop, or server you want to monitor.

### 1. Build the Standalone `.exe` (On Admin PC)
Run this command on your main Admin computer:
```bash
cd prism-agent
python build_exe.py
```
This auto-detects your Admin PC's IP address (`http://<ADMIN_IP>:8000`) and generates **`prism-agent/dist/prism-agent.exe`** and **`.env.agent`**.

### 2. Deploy to User / Target Computers
1. Copy **`prism-agent.exe`** and **`.env.agent`** onto a USB flash drive or transfer across the network to the target computer.
2. On the target computer, right-click **`prism-agent.exe`** and select **"Run as Administrator"** *(Required for network card packet capture privileges)*.

### 3. What the User Machine Does Automatically:
- **Zero Configuration**: No Python, Git, or manual configuration required on target machines.
- **Silent Background Telemetry**: Reads machine hostname (e.g., `FINANCE-LAPTOP`), local IP, and hardware specs, then registers automatically with your Central Admin Server.
- **Real-Time Protection**: Continuously analyzes local packet traffic using Scapy + Random Forest ML and streams threat telemetry back to your Admin Dashboard!

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
                                (24-Feature Vector Extraction)
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

---

## 📦 Standalone Windows `.exe` Agent Build

You can bundle the sensor agent into a **single 34 MB standalone Windows `.exe` file** (`prism-agent.exe`) that requires **NO Python or Git installation** on target systems!

### ⚙️ How to Build `prism-agent.exe`:
```bash
cd prism-agent
python build_exe.py
```

---

## 🤖 AI Security Analyst (Ollama)

The PRISM AI Analyst endpoints expose local LLM capabilities via `/api/ai/*`:

### Endpoints Overview

#### 1. AI Health Check
```http
GET /api/ai/health
```

#### 2. Alert Explanation & MITRE Mapping
```http
POST /api/ai/alert/{alert_id}/summary
```

#### 3. Interactive Analyst Chat (SSE Streaming)
```http
POST /api/ai/chat
```

---

## 🔧 Troubleshooting & FAQ

| Issue / Error | Root Cause | Solution |
| :--- | :--- | :--- |
| **`failed to connect to docker API... daemon not running`** | Docker Desktop application is closed. | Launch **Docker Desktop** from Windows Start Menu and wait until engine status turns green. |
| **`Connect call failed ('127.0.0.1', 5432)`** | PostgreSQL database service is stopped. | Run `docker-compose up -d postgres` or start `postgresql-x64-16` in Windows Services. |
| **`'vite' is not recognized as an internal command`** | Node packages not installed in `prism-dashboard`. | Run `npm.cmd install` (or `npm install`) inside `prism-dashboard` folder first. |
| **`ModuleNotFoundError: No module named 'agent'`** | Python current directory import path issue. | Run `python -m agent.main` from inside the `prism-agent` directory. |
| **Scapy Packet Capture Permission Error** | Non-Administrator privileges on Windows/Linux. | Right-click terminal / `prism-agent.exe` and select **"Run as Administrator"** (or use `sudo` on Linux). |

---

## 📜 License

PRISM IDS is licensed under the **[MIT License](LICENSE)**.

<div align="center">
  <sub>Developed with ❤️ by the PRISM IDS Security Engineering Team.</sub>
</div>
