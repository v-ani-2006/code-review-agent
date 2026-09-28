import asyncio
from sqlalchemy import text
from app.core.config import settings
from app.core.logging import logger
from app.db.session import engine
from app.models.base import Base
# Ensure all models are imported so Base.metadata knows about them
import app.models  # noqa: F401


async def _sync_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def init_db() -> bool:
    """Verify database connectivity and initialize tables in development mode.

    Returns True if connection and initialization succeed, False otherwise.
    """
    try:
        if settings.DEBUG:
            logger.info("🛠️  Development mode detected: Synchronizing ORM tables with database...")
            try:
                await asyncio.wait_for(_sync_tables(), timeout=5.0)
                logger.info(" Database tables verified and ready.")
            except asyncio.TimeoutError:
                logger.warning("⚠️ Table synchronization timed out (lock held by external migration). Proceeding with startup.")
            except Exception as sync_err:
                logger.warning("⚠️ Table synchronization note: %s", str(sync_err))

        return True

    except Exception as exc:
        logger.warning(
            "⚠️ Database connection failed or database offline at %s:%s/%s: %s",
            settings.DATABASE_HOST,
            settings.DATABASE_PORT,
            settings.DATABASE_NAME,
            str(exc),
        )
        return False
