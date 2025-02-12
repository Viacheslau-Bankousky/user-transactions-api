"""
This module provides utils for managing async database sessions.

The primary function, `get_session`, serves as an async context
manager to establish and manage the lifecycle of database sessions.
Sessions are created using the `engine` and `AsyncSessionMaker`
configured for asynchronous operations with the database.

Key Features:
-------------
- Ensures proper management of session resources, including creation,
 committing transactions, rolling back when errors occur, and closing
 sessions.
- Logs key lifecycle stages, providing more traceability and aiding in
 debugging.
- Simplifies separation of logic between production and testing
 environments.

Components:
-----------
1. `engine`: The asynchronous database engine.
2. `AsyncSessionMaker`: A session factory configured with the engine,
 used for creating asynchronous sessions.
3. `get_session`: An async context manager that manages session lifecycle
 (creation, commit, rollback, and close).

Usage:
------
- Use `get_session` in your application to interact safely with the database.
- The session factory (`AsyncSessionMaker`) automatically uses the production
 engine settings.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.base_settings import settings
from core.logger_configuration import app_logger

engine: AsyncEngine = create_async_engine(
    settings.db_url,
    echo=True,
)

AsyncSessionMaker: Callable[..., AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an asynchronous context manager for managing database sessions.

    This function creates and manages the lifecycle of an asynchronous
    database session.
    It ensures:
    - Sessions are created using the configured `AsyncSessionMaker`.
    - Successful transactions are committed automatically.
    - Transactions are rolled back in case of exceptions.
    - Sessions are properly closed after their usage.

    Logs are generated at each stage of the session lifecycle, aiding
    in traceability and debugging.

    Yields:
        AsyncGenerator[AsyncSession, None]: An asynchronous database session
        ready for operations.

    Raises:
        Exception: If an error occurs during the session
            (e.g., a failed database operation).
            The exception is propagated after rolling back
            the transaction.

    Example:
        ```python
        async with get_session() as session:
            # Perform database operations
            result = await session.execute(my_query)
            data = result.fetchall()
        ```
    """
    app_logger.info("Establishing database session")
    session = AsyncSessionMaker()

    try:
        yield session
        await session.commit()
        app_logger.info("Database session commit successful")
    except Exception as ex:
        app_logger.exception("An error occurred with the database session")
        await session.rollback()
        raise ex
    finally:
        await session.close()
        app_logger.info("Database session closed")
