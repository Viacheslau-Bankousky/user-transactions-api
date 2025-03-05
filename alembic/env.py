"""
This module provides functionality for running database migrations.

Database configuration is dynamically loaded based on the `sqlalchemy.url`
template defined in the Alembic configuration file. The template is dynamically
formatted with database user credentials (`DB_USER` and `DB_PASSWORD`) which
are provided via environment variables. SQLAlchemy models' metadata and
connection parameters are configured to ensure smooth and reliable execution
of migrations.

Key Functions:
- `run_migrations_offline()`: Executes migrations in "offline" mode, where
  no active database connection is required. SQL commands are generated as
  output strings.
- `do_run_migrations()`: Provides the core logic for executing migrations
  within
  a given database connection context.
- `run_async_migrations()`: Executes migrations using an async database
  connection and runs them asynchronously against the database.
- `run_migrations_online()`: Triggers the migration process in "online" mode,
  using an actual database connection.

Usage:
The module determines whether to run in "offline" or "online" mode based on the
current context (`context.is_offline_mode()`). Migrations can also be executed
asynchronously using an async-engine setup.

Environment Variables:
- `DB_USER`: The database username, injected dynamically in the connection URL.
- `DB_PASSWORD`: The database password, injected dynamically in the connection
   URL.

Configuration:
- Alembic configuration templates (e.g., `sqlalchemy.url`) are required to
  contain placeholders for `DB_USER` and `DB_PASSWORD`, which will be replaced
  at runtime.
"""

import asyncio
from logging.config import fileConfig
from typing import Optional

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from core.base_settings import settings  # type: ignore
from core.models import Base  # type: ignore

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given
    string to the script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Execute migrations within a provided connection context.

    This function configures connection context and target metadata,
    begins a transaction and runs migrations on the provided connection.

    Args:
        connection (Connection):
            The connection to the database where migrations will be run.
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Execute migrations asynchronously within a connection context.

    This function configures the connection URL with the database
    user and password, creates a connection using async SQLAlchemy
    engine, and runs the migrations asynchronously.
    After the migrations have been run, the connection to the
    database is closed.
    """
    url: Optional[str] = config.get_main_option("sqlalchemy.url")
    if url is not None:
        config.set_main_option(
            "sqlalchemy.url",
            url.format(settings.DB_USER, settings.DB_PASSWORD),
        )
        connectable = async_engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

        await connectable.dispose()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    This function runs the migrations asynchronously on an actual
    connection to the database.
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
