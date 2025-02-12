"""This module sets up basic Fixtures for the pytest to use during testing."""

from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import engine as test_engine
from core.database import get_session
from core.models import Base
from tests.common.app_for_testing import testing_app as test_app


@pytest_asyncio.fixture(scope="function", autouse=True)
async def set_up_testing_database() -> AsyncGenerator:
    """
    Use to set up the testing database before each test.

    Done by creating all tables in the Base metadata using the test_engine.

    Yields:
        None.
        After setting up, surrenders control back to the test execution.
        Automatically used due to 'autouse=True'.
    """
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture(scope="function")
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an instance of AsyncSession.

    This fixture is automatically applied to all tests due to
    `autouse=True`.
    It creates and yields a new database session using the
    `get_session` function.
    After the test is complete, the session is automatically closed.

    Yields:
        AsyncSession: An instance of the asynchronous database session.
    """
    async with get_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Yield an AsyncClient object that tests can use to make requests.

    Yields:
        An instance of AsyncClient.
    """
    async with AsyncClient(
        base_url="http://test_fastapi",
        transport=ASGITransport(app=test_app),  # type: ignore
    ) as async_client:
        yield async_client


@pytest_asyncio.fixture(scope="function", autouse=True)
async def teardown_testing_database() -> AsyncGenerator:
    """
    Use to clean up the testing database after each test.

    Done by dropping all tables in the Base metadata using the test_engine.

    Yields:
        None.
        After the tear-down is complete, surrenders control back to the test
        execution.
        Automatically used due to 'autouse=True'.
    """
    yield
    async with test_engine.begin() as cleanup_connection:
        await cleanup_connection.run_sync(Base.metadata.drop_all)

