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

[Architecture](#-system-architecture) • [AI Analyst Role](#-ai-security-analyst-how-it-works--whats-its-use) • [Admin Guide](#-admin-end-guide-central-soc-master) • [User Guide](#-user-end-guide-target-device-sensor) • [Deployment](#-getting-started--deployment) • [Executable (.exe)](#-standalone-windows-exe-agent-build) • [Troubleshooting](#-troubleshooting--faq)

</div>

---

## 👁️ System Overview

**PRISM IDS** is a high-performance cyber threat detection platform engineered for modern enterprise environments. It combines raw packet acquisition, canonical 5-tuple flow generation, 24-dimensional feature extraction, dual signature & Scikit-Learn Random Forest Machine Learning detection, normalized risk scoring ($0-100$), and automated threat deduplication into a unified security operations platform.

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

### 🎯 Key Capabilities & Use Cases

#### 1. Real-Time Threat Briefings (`POST /api/ai/alert/{alert_id}/summary`)
When an administrator clicks **"AI Analyze (👁️)"** on any live alert, the AI analyzes the alert payload and generates:
- **Executive Summary**: High-level overview of the incident.
- **Technical Root Cause**: Specific explanation of why the threshold was crossed (e.g. *"Host 192.168.1.50 sent 4,500 SYN packets/sec without completing handshakes"*).
- **MITRE ATT&CK Mapping**: Identifies the exact tactic and technique ID (e.g. `T1498 Network Denial of Service`, `T1046 Network Service Discovery`, `T1110 Brute Force`, `T1190 Exploit Public-Facing Application`).
- **Remediation Action Plan**: Step-by-step containment instructions and ready-to-run firewall command strings.

#### 2. Interactive SOC Chat Assistant (`POST /api/ai/chat`)
An interactive streaming chat interface (`POST /api/ai/chat?stream=true`) that lets administrators talk directly with the AI:
- Ask follow-up questions: *"How do I harden my web server against this SYN flood?"* or *"What other ports were probed?"*.
- Receive live real-time token streaming responses on the dashboard.

#### 3. Executive PDF & JSON Security Reports (`POST /api/ai/report`)
Generates comprehensive audit-ready incident reports summarizing top attacking IPs, target hosts, threat distribution, and recommended long-term security posture improvements for management.

---

### ⚙️ How the AI Operates Under the Hood

1. **Strict L3 SOC Analyst Persona Prompt**: System prompts constrain the model to operate as a senior security specialist, guaranteeing high-precision technical answers.
2. **In-Memory `LLMCache`**: Hashes alert telemetry signatures so duplicate/recurring attack patterns receive **instant 0ms cached responses** without wasting CPU cycles.
3. **Graceful Fallback Resilience**: If Ollama is turned off or not installed, PRISM IDS automatically falls back to deterministic rule-based threat descriptions so the system never crashes.

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
