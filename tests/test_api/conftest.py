"""
Module for setting up asynchronous fixtures for testing.

This module defines an asynchronous pytest fixture that automatically adds
new users to the system before each test function.
"""

from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy import select

from authentication.user_management import check_user_has_token
from models.users import User, UserBalance
from tests.common.app_for_testing import testing_app as test_app
from tests.utils.mocks import mock_token_dependency
from tests.utils.test_data_setup import add_balances, add_users

USER_ID = USER_BALANCE_ID = 1

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


@pytest_asyncio.fixture
async def overridden_dependency() -> AsyncGenerator:
    test_app.dependency_overrides[check_user_has_token] = mock_token_dependency
    yield
    test_app.dependency_overrides = {}


@pytest_asyncio.fixture
async def initial_user_balance(async_db_session) -> UserBalance:
    query = select(UserBalance).where(
        UserBalance.id == USER_BALANCE_ID,
        UserBalance.user_id == USER_ID,
    )
    user_balance = await async_db_session.execute(query)
    return user_balance.scalar_one()
