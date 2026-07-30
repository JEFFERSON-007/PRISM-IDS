# Setup & Environment Guide

## Prerequisites

- Python 3.12 or higher
- PostgreSQL 16+ (or Docker Compose)
- `uv` (recommended) or `pip` / `poetry`
- Docker & Docker Compose (optional for containerized setup)

---

## Environment Setup Step-by-Step

### Step 1: Clone & Navigate

```bash
cd "c:/Users/mariy/OneDrive/Documents/extra tasks i do when i am bored/PRISM IDS"
```

### Step 2: Configure Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Ensure `DATABASE_URL` matches your PostgreSQL connection credentials:
```env
DATABASE_URL="postgresql+asyncpg://prism_user:prism_secure_password@localhost:5432/prism_ids_db"
```

### Step 3: Install Dependencies

Using `pip`:
```bash
pip install -e ".[dev]"
```

Using `uv`:
```bash
uv pip install -e ".[dev]"
```

### Step 4: Run Alembic Database Migrations

```bash
alembic upgrade head
```

### Step 5: Start Local Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Docker Compose Setup

To start both PostgreSQL and FastAPI in isolated containers:

```bash
# Production mode
docker-compose up --build -d

# Development mode with live reload
docker-compose -f docker-compose.dev.yml up --build
```
