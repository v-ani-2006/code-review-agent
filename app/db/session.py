from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.logging import logger

# Create the asynchronous SQLAlchemy engine with robust pooling configuration
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,    # Tests connections for liveness before issuing queries
    pool_recycle=3600,     # Recycles connections every hour to avoid server disconnects
    future=True,
)

# Async session factory configured for non-expiring commits and explicit transactions
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Alias for standard naming compatibility
async_session_maker = AsyncSessionLocal



async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an asynchronous database session.

    Guarantees automatic rollback on unhandled exceptions and deterministic session closing.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as exc:
            logger.error("Database session transaction aborted due to exception: %s", str(exc))
            await session.rollback()
            raise
        finally:
            await session.close()
