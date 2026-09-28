import asyncio
from logging.config import fileConfig
from pathlib import Path
import sys

# Ensure project root is in sys.path so 'app' is importable from anywhere
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings
from app.core.logging import logger
# Import Base and models to ensure all table metadata is registered
from app.models.base import Base
from app.models.user import User  # noqa: F401
from app.models.review import Review  # noqa: F401

# Alembic Config object, which provides access to the values within the .ini file
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Overwrite sqlalchemy.url with dynamic ASYNC_DATABASE_URL from application settings
config.set_main_option("sqlalchemy.url", settings.ASYNC_DATABASE_URL)

# Model metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the context with just a URL and not an Engine.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        logger.info("Executing offline migration...")
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    try:
        import sqlalchemy as sa
        connection.execute(sa.text("ALTER TABLE IF EXISTS alembic_version ALTER COLUMN version_num TYPE VARCHAR(64);"))
        connection.commit()
    except Exception:
        pass

    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        logger.info("Executing database migration transaction...")
        context.run_migrations()
        logger.info("Database migration completed successfully.")


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode using asynchronous SQLAlchemy engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
