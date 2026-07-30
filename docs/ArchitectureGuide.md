# Technical Architecture Guide

PRISM IDS follows Clean Architecture principles:

- **Domain Layer**: Pure business models, rules, and value objects (`app/domain/`, `prism-agent/agent/capture/packet_models.py`, `flow_models.py`).
- **Repository Layer**: Encapsulated database queries via SQLAlchemy 2.0 Async Session (`app/repositories/`).
- **Service Layer**: Business logic workflows (`app/services/`).
- **API Controller Layer**: FastAPI endpoints with Pydantic validation and JWT protection (`app/api/v1/endpoints/`).
- **Presentation Layer**: Obsidian Dark React 19 SOC Dashboard (`prism-dashboard/`).
