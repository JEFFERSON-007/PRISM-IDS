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

[Architecture](#-system-architecture) • [User Windows App Guide](#-user-end-guide-windows-app-installation--configuration) • [Admin SOC Guide](#-admin-end-guide-central-soc-master) • [AI Analyst Role](#-ai-security-analyst-how-it-works--whats-its-use) • [Deployment](#-getting-started--deployment) • [Executable Build](#-standalone-windows-exe-agent-build) • [Troubleshooting](#-troubleshooting--faq)

</div>

---

## 👁️ System Overview

**PRISM IDS** is a high-performance cyber threat detection platform engineered for modern enterprise environments. It combines raw packet acquisition, canonical 5-tuple flow generation, 24-dimensional feature extraction, dual signature & Scikit-Learn Random Forest Machine Learning detection, normalized risk scoring ($0-100$), and automated threat deduplication into a unified security operations platform.

---

## 👨‍💻 USER-END GUIDE (Windows App Installation & Configuration)

The **User End App** (`prism-agent.exe`) is a lightweight standalone Windows executable installed on target computers, employee laptops, or servers that you want to monitor.

### 📥 1. Direct Download
- **`prism-agent.exe`**: [Download Standalone Executable (GitHub Direct)](https://github.com/JEFFERSON-007/PRISM-IDS/raw/main/prism-agent/dist/prism-agent.exe)
- **`.env.agent`**: [Download Configuration File](https://github.com/JEFFERSON-007/PRISM-IDS/raw/main/prism-agent/.env.agent)

---

### 🚀 2. Step-by-Step Windows Installation Guide

1. **Create Destination Folder**:
   Create a dedicated folder on the target Windows computer (e.g. `C:\PRISM-Agent\`).

2. **Paste Downloaded Files**:
   Copy both **`prism-agent.exe`** and **`.env.agent`** into `C:\PRISM-Agent\`.

3. **Launch with Administrator Privileges**:
   Right-click **`prism-agent.exe`** and select **"Run as Administrator"**.
   > ⚠️ **Why Administrator Rights are Required**: Windows packet sniffing drivers (Scapy / Npcap) require elevated privileges to access raw network interface cards.

---

### ⚙️ 3. Configuration Breakdown (`.env.agent`)

The **`.env.agent`** file controls how the sensor communicates with your Central Admin Server:

```env
# ==============================================================================
# PRISM IDS Sensor Agent Configuration
# ==============================================================================

# Custom sensor name (Leave default to automatically use Windows Hostname e.g. DESKTOP-FINANCE)
AGENT_NAME="remote-agent-sensor"

# Central Admin Server URL (Auto-detected during build or manually set to your server IP)
SERVER_URL="http://10.3.2.16:8000"

# Heartbeat Telemetry interval in seconds (Reports CPU/RAM health to Admin Dashboard)
HEARTBEAT_INTERVAL=15

# Automatic server reconnection retry interval in seconds
RECONNECT_INTERVAL=5

# HTTP API request timeout in seconds
HTTP_TIMEOUT=10.0

# Local credentials storage file
CREDENTIALS_FILE=".agent_credentials.json"

# Logging configuration
LOG_LEVEL="INFO"
LOG_FORMAT="json"
LOG_DIR="logs"
DEBUG=true
TIMEZONE="UTC"
```

| Configuration Parameter | Default Value | Purpose |
| :--- | :--- | :--- |
| **`SERVER_URL`** | `http://<ADMIN_IP>:8000` | Points to your Central Admin Server IP address. |
| **`AGENT_NAME`** | `remote-agent-sensor` | Custom display name. If default, automatically uses machine hostname (e.g. `DESKTOP-8492AK`). |
| **`HEARTBEAT_INTERVAL`** | `15` | Frequency (seconds) of sending CPU, RAM, and Disk health metrics to the Dashboard. |
| **`RECONNECT_INTERVAL`**| `5` | Retry delay (seconds) if connection to Central Server drops. |
| **`CAPTURE_ENABLED`** | `true` | Enables real-time Scapy network packet capture. |

---

### 🔁 4. Run Automatically at Windows Startup (Optional)

To ensure `prism-agent.exe` starts automatically every time the Windows PC boots up:

1. Press `Win + R`, type **`taskschd.msc`**, and press Enter.
2. Click **Create Task** on the right sidebar.
3. Under **General**:
   - Name: `PRISM-IDS-Agent`
   - Check **"Run with highest privileges"** *(Required for admin rights)*.
4. Under **Triggers**:
   - New Trigger → Begin the task: **At startup** (or **At log on**).
5. Under **Actions**:
   - Action: **Start a program**
   - Program/script: Browse to `C:\PRISM-Agent\prism-agent.exe`
   - Start in: `C:\PRISM-Agent\`
6. Click **OK**. The agent will now run silently in the background every time Windows turns on!

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

## 🤖 AI SECURITY ANALYST: HOW IT WORKS & WHAT'S ITS USE

The **AI Security Analyst** is powered by a local Large Language Model (**Ollama `qwen2.5:3b`**) integrated directly into the PRISM Central Server (`app/llm/`).

### 💡 Why is the AI Used? (Purpose & Business Impact)
Raw Intrusion Detection System logs consist of complex numerical data: TCP flag ratios, BPF bytecode, packet rate variances, and Shannon entropy values ($H(X)$). Interpreting these numbers usually requires senior Level-3 cybersecurity specialists. 

The AI Security Analyst acts as an **always-on Level-3 SOC Security Analyst**:
- **Translates Technical Logs into Human Language**: Explains complex network attacks in plain, executive-friendly English.
- **100% Privacy & On-Premises Control**: Runs **100% locally** via Ollama. No IP addresses, network telemetry, or private data ever leave your central server.
- **Standardized Threat Mapping**: Automatically maps detected anomalies to official **MITRE ATT&CK** industry frameworks.
- **Instant Incident Remediation**: Provides copy-paste firewall rules (e.g. `iptables` or Windows Firewall commands) so system administrators can block attacks in seconds.

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

---

## 📦 Standalone Windows `.exe` Agent Build

You can bundle the sensor agent into a **single 34 MB standalone Windows `.exe` file** (`prism-agent.exe`) that requires **NO Python or Git installation** on target systems!

### ⚙️ How to Build `prism-agent.exe`:
```bash
cd prism-agent
python build_exe.py
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
