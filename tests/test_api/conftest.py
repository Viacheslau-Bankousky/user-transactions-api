"""
Module for setting up asynchronous fixtures for testing.

This module defines an asynchronous pytest fixture that automatically adds
new users to the system before each test function.
"""

import pytest_asyncio
from utils.test_data_setup import add_balances, add_users

from models.users import User


@pytest_asyncio.fixture(scope="function", autouse=True)
async def users(async_db_session) -> None:
    """
    Add new users and their balances to the database.

    This fixture automatically executes before each test function due
    to `autouse=True`.
    It uses the provided `async_db_session` to interact with the database
    by adding new users and their corresponding balances.

    Args:
        async_db_session (AsyncSession): An active database session used
            for adding users and balances.
    """
    new_users: list[User] = await add_users(async_db_session)
    await add_balances(async_db_session, new_users)
