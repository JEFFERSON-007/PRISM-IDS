# Repository Folder Structure

```
c:\Users\mariy\OneDrive\Documents\extra tasks i do when i am bored\PRISM IDS/
├── app/
│   ├── api/                     # Presentation Layer: FastAPI REST & Dependencies
│   │   ├── dependencies.py      # Dependency Injection providers (DB, Auth, Logger, Settings)
│   │   └── v1/
│   │       ├── router.py        # API v1 Router Aggregator
│   │       └── endpoints/       # Endpoint implementations
│   │           ├── auth.py      # Auth foundation test endpoints
│   │           ├── health.py    # Health, Readiness, & Liveness probes
│   │           ├── status.py    # System overview status
│   │           └── websocket.py # WebSocket connection endpoint
│   ├── authentication/          # Authentication Foundation (JWT, Passwords, RBAC)
│   │   ├── jwt.py               # Token creation, decoding, & verification
│   │   ├── password.py          # Secure password hashing (Argon2 / Bcrypt)
│   │   ├── permissions.py       # Fine-grained permissions & matrix
│   │   └── roles.py             # System Role Enum
│   ├── core/                    # Core Infrastructure
│   │   ├── config.py            # Pydantic Settings v2 configuration
│   │   ├── exceptions.py        # Custom Exception hierarchy & FastAPI error handlers
│   │   ├── logging.py           # Structlog setup & rotating log handlers
│   │   └── security.py          # High-level security helpers
│   ├── database/                # Database Foundation
│   │   ├── base.py              # Declarative Base model with UUID & timestamps
│   │   ├── session.py           # Async SQLAlchemy Engine, pool, & health checks
│   │   └── migrations/          # Alembic async database migration environment
│   ├── domain/                  # Domain Layer Interfaces
│   │   └── interfaces/          # Generic Abstract Repository & Service Interfaces
│   │       ├── repository.py    # IRepository generic contract
│   │       └── service.py       # IService generic contract
│   ├── middlewares/             # HTTP Pipeline Middlewares
│   │   ├── error_handler.py     # Global error interceptor
│   │   ├── logging.py           # Structured request/response logger
│   │   ├── request_id.py        # X-Request-ID & X-Correlation-ID injector
│   │   ├── security_headers.py  # Enterprise security headers enforcer
│   │   └── timing.py            # Latency process time header
│   ├── repositories/            # Data Access Concrete Repositories
│   │   └── base.py              # BaseRepository SQLAlchemy implementation
│   ├── schemas/                 # Pydantic v2 DTO Data Validation Schemas
│   │   ├── base.py              # Generic response envelope model
│   │   ├── error.py             # Error response schemas
│   │   ├── health.py            # Probe & status output schemas
│   │   └── token.py             # JWT Token models
│   ├── services/                # Application Layer Services
│   │   └── base.py              # BaseService generic implementation
│   ├── utils/                   # Shared Reusable Utilities
│   │   ├── datetime.py          # UTC timezone helpers
│   │   ├── json.py              # JSON encoder for UUID & Datetimes
│   │   ├── pagination.py        # Pagination request & response helpers
│   │   ├── response.py          # Standardized response builders
│   │   └── uuid.py              # UUID generation and validation
│   ├── websocket/               # WebSocket Real-Time Infrastructure
│   │   └── manager.py           # ConnectionManager for clients, channels, & heartbeat
│   └── main.py                  # FastAPI Application Factory & Lifespan
├── docker/                      # Docker assets
│   ├── Dockerfile               # Multi-stage production container build
│   ├── docker-compose.yml       # Production docker compose configuration
│   └── docker-compose.dev.yml   # Live-reload development compose
├── docs/                        # Enterprise Architecture Documentation
│   ├── API.md
│   ├── Architecture.md
│   ├── CodingStandards.md
│   ├── Development.md
│   ├── FolderStructure.md
│   └── Setup.md
├── tests/                       # Automated Test Suite (Pytest)
│   ├── conftest.py              # Pytest async fixtures
│   ├── integration/             # Endpoint integration tests
│   └── unit/                    # Unit tests for security, config, websocket
├── .env.example                 # Environment configuration template
├── .gitignore
├── alembic.ini                  # Alembic CLI config
├── pyproject.toml               # Project metadata & dependencies
└── README.md                    # Project overview & quickstart
```
