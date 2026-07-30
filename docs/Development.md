# Development Workflow & Guidelines

## 1. Code Formatting & Linting

PRISM IDS strictly adheres to PEP8 and uses `ruff` and `black`.

Run ruff linter:
```bash
ruff check .
```

Auto-fix linting issues:
```bash
ruff check --fix .
```

Format code:
```bash
black .
```

Type checking:
```bash
mypy app
```

---

## 2. Database Migrations with Alembic

Create a new migration revision after modifying models:
```bash
alembic revision --autogenerate -m "describe changes"
```

Apply migrations to database:
```bash
alembic upgrade head
```

Rollback last migration:
```bash
alembic downgrade -1
```

---

## 3. Running Pytest Suite

Run all tests:
```bash
pytest
```

Run only unit tests:
```bash
pytest tests/unit
```

Run only integration tests:
```bash
pytest tests/integration
```
