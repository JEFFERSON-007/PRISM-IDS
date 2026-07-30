# Installation Guide

## Prerequisites

- Python 3.12+
- Node.js 20+ & npm
- PostgreSQL 16+
- Docker & Docker Compose
- Npcap (Windows) or libpcap-dev (Linux)

## Local Manual Setup

1. **Database Setup**:
   Create PostgreSQL database `prism_ids_db` and user `prism_user`.

2. **Server Installation**:
   ```bash
   pip install -r pyproject.toml
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

3. **Frontend Dashboard Setup**:
   ```bash
   cd prism-dashboard
   npm install
   npm run dev
   ```

4. **Agent Installation**:
   ```bash
   cd prism-agent
   pip install -r pyproject.toml
   python -m agent.main
   ```
