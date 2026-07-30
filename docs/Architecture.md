# PRISM IDS Architecture Specification

## Clean Architecture Layers

PRISM IDS enforces Clean Architecture principles with inward-pointing dependencies. Inner layers do not import from outer layers.

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  FastAPI Routers (/api/v1) │ WebSockets (/ws/v1/connect)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    Application Layer                        │
│   Services (BaseService) │ Use Cases │ Schemas (Pydantic v2) │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                      Domain Layer                           │
│  Interfaces (IRepository, IService) │ Entities │ RBAC Enums  │
└──────────────────────────────▲──────────────────────────────┘
                               │
┌──────────────────────────────┴──────────────────────────────┐
│                   Infrastructure Layer                      │
│   SQLAlchemy 2.0 Async Session │ JWT Auth │ Structlog Logs  │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Domain Layer (`app/domain/`)
- Contains enterprise business rules, abstract contracts (`IRepository`, `IService`), and domain models.
- Completely decoupled from external frameworks, database drivers, or HTTP routers.

## 2. Application Layer (`app/services/` & `app/schemas/`)
- Encapsulates use cases and application logic.
- Maps domain objects into type-safe Pydantic schemas.

## 3. Presentation Layer (`app/api/` & `app/websocket/`)
- Handles HTTP requests, input validation, serialization, and WebSocket connections.
- Utilizes FastAPI Dependency Injection (`app/api/dependencies.py`) to inject services, database sessions, and authenticated context.

## 4. Infrastructure Layer (`app/database/`, `app/core/`, `app/authentication/`)
- Provides concrete implementations for database access (`BaseRepository`), password hashing (Argon2 / Bcrypt), JWT encoding/decoding, structured logging, and HTTP middleware pipelines.
