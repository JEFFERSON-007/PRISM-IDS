# Coding Standards & Guidelines

PRISM IDS maintains strict enterprise production standards across all components.

## Core Rules

1. **Strict Type Hinting**: Every function, method, and variable definition must contain explicit type hints (`str`, `int`, `Optional[T]`, `AsyncGenerator`, etc.).
2. **No Placeholders**: `TODO`, `Coming Soon`, or dummy stubs are strictly forbidden in production commits.
3. **No Global State**: Dependencies must be injected via FastAPI's `Depends()` or class instantiation.
4. **Explicit Exception Raising**: Use custom application exceptions defined in `app/core/exceptions.py` (`AuthenticationError`, `PermissionDeniedError`, `PRISMValidationError`, `DatabaseError`, `NotFoundError`). Never raise bare `Exception`.
5. **No Business Logic in Routes**: API routers (`app/api/v1/endpoints/`) are presentation layers only. They deserialize input via Pydantic schemas, call application services, and return responses.
6. **Structured Logging**: Always use `structlog` loggers. Inject contextual parameters as keyword arguments (`logger.info("Event occurred", user_id=uid)`), never string interpolation.
7. **Clean Imports**: No circular imports. Group imports into standard library, third-party packages, and internal application packages sorted alphabetically.
