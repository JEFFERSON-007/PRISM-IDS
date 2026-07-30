"""Async SQLAlchemy Engine, Session Factory, and Health Check utilities."""

import time
from typing import AsyncGenerator, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
import structlog
from app.core.config import settings
from app.core.exceptions import DatabaseError

logger = structlog.get_logger("prism_ids.database")

# Create Async Engine with connection pooling and auto-reconnect (pool_pre_ping=True)
engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,
)

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
                    "pool_size": settings.DB_POOL_SIZE,
                }
            return {"status": "unhealthy", "error": "Unexpected scalar query result"}
    except Exception as exc:
        logger.error("Database health check failed", error=str(exc))
        return {
            "status": "unhealthy",
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
            "error": str(exc),
        }
