"""Isolated database fixtures with automatic per-test transaction rollback."""
from typing import AsyncGenerator
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Dedicated test engine using NullPool to prevent connection reuse across different asyncio event loops
test_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an isolated database session with full rollback on teardown.

    Guarantees that database mutations during a test are completely rolled back,
    preventing any test interference or persistence into the main database.
    """
    connection = await test_engine.connect()
    trans = await connection.begin()

    session_maker = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
        join_transaction_mode="create_savepoint",
    )

    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
            if trans.is_active:
                await trans.rollback()
            await connection.close()
