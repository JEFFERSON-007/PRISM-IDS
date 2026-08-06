"""Async SQLAlchemy Engine, Session Factory, and Health Check utilities."""

import time
from typing import AsyncGenerator, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
import structlog
from app.core.config import settings
from app.core.exceptions import DatabaseError

logger = structlog.get_logger("prism_ids.database")

# Dynamic engine parameters based on database driver (SQLite vs PostgreSQL)
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
engine_kwargs: Dict[str, Any] = {"echo": settings.DEBUG}

if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    })

# Create Async Engine with auto-reconnect
try:
    engine = create_async_engine(
        url=settings.DATABASE_URL,
        **engine_kwargs,
    )
except ModuleNotFoundError as exc:
    logger.warning(
        "Database driver module missing. Install required driver package.",
        error=str(exc),
        url=settings.DATABASE_URL,
    )
    # Fallback engine definition
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", connect_args={"check_same_thread": False})

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency generator providing a transactional async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.error("Database session transaction rolled back due to error", error=str(exc))
            raise DatabaseError(message=f"Database transaction error: {str(exc)}") from exc
        finally:
            await session.close()


# Alias for dependency injection compatibility
get_db = get_db_session


async def check_database_health() -> Dict[str, Any]:
    """Perform connection health check and measure round-trip latency."""
    start_time = time.perf_counter()
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            val = result.scalar()
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            if val == 1:
                return {
                    "status": "healthy",
                    "latency_ms": latency_ms,
                    "database_type": "SQLite" if is_sqlite else "PostgreSQL",
                }
            return {"status": "unhealthy", "error": "Unexpected scalar query result"}
    except Exception as exc:
        logger.error("Database health check failed", error=str(exc))
        return {
            "status": "unhealthy",
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
            "error": str(exc),
        }
