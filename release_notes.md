# PRISM IDS v1.0.0 — Official Production Release

Welcome to the v1.0.0 Production Release of PRISM IDS (Predictive Reasoning & Intelligent Security Monitoring).

PRISM IDS is an enterprise-grade, real-time Intrusion Detection System & SOC Dashboard platform powered by Scapy network sensors, Random Forest Machine Learning, Signature Rules, and a Local Ollama AI Security Analyst (`qwen2.5:3b`).

---

### Key Features in v1.0.0

- **Standalone Portable Windows Agent (`prism-agent.exe`)**:
  - Self-contained executable requiring no Python, Git, or manual installation on target PCs.
  - Multi-source server URL resolution: command line flags (`--server-url`), environment variables (`PRISM_SERVER_URL`), local JSON config (`prism_agent_config.json`), or interactive auto-setup wizard on first run.
  - Portable PyInstaller path resolution for ML models (`prism_ids_rf.joblib`), signature rules, credentials, and logs.
  - Fault-isolated Scapy packet sniffing with graceful telemetry fallback if Npcap is missing.

- **Hybrid Threat Detection (Signature + Machine Learning)**:
  - Real-time 24-feature vector extraction (packet rates, TCP flag ratios, Shannon Entropy $H(X)$).
  - Multithreaded Random Forest ML model running on background worker pools for wire-speed packet analysis.

- **Local Ollama AI Security Analyst (`qwen2.5:3b`)**:
  - 100% On-Premises Privacy: No network data or IP addresses leave your server.
  - Explains attack telemetry in plain English, maps threats to MITRE ATT&CK (T1498, T1046, T1110, T1190), and generates ready-to-use firewall drop rules.
  - Real-time SSE streaming chat interface (`POST /api/ai/chat?stream=true`).

- **React 19 Dark Obsidian SOC Dashboard**:
  - Live WebSocket alert feeds, real-time threat analytics, and agent fleet tracking.

---

### Quick Start Guide

#### For User Target Computers (Windows Sensor)
1. Download `prism-agent.exe` from the Assets section below.
2. Double-click `prism-agent.exe` or run as Administrator.
3. If running for the first time, it will auto-detect or prompt for your Central Admin Server URL (e.g. `http://192.168.1.50:8000`), save it, and start streaming telemetry automatically.

#### For Central Admin Server (SOC HQ)
```bash
git clone https://github.com/JEFFERSON-007/PRISM-IDS.git
cd PRISM-IDS
docker-compose up --build -d
```
