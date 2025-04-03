"""
Asynchronous Testing Fixtures Module.

This module provides pytest fixtures for setting up and managing test data
asynchronously in the context of database-backed tests. The fixtures are
primarily designed to streamline setup operations for user, balance, and
dependency management in test cases.

Key Features:
- **Automatic User Setup**: Automatically adds test users and their balances
  before each test function.
- **Dependency Overrides**: Overrides specific application dependencies to
  enable mocking during tests.
- **Balance Retrieval**: Simplifies queries for retrieving initial user
  balances from the database.

Dependencies:
- `pytest_asyncio`: For defining asynchronous pytest fixtures.
- `SQLAlchemy`: Used for database operations, including user and balance
    queries.
- `tests.common.app_for_testing.testing_app`: The test application
  instance for overriding dependencies.
- `authentication.user_management.check_user_has_token`: Dependency method
  overridden in tests to mock token validation.
- `tests.utils.test_data_setup`: Helper methods for creating database test
 data, such as `add_balances` and `add_users`.

Constants:
- **USER_ID**: A constant representing a test user ID (default: `1`).
- **USER_BALANCE_ID**: A constant representing a test user balance ID
 (default: `1`).

Examples:
These fixtures are used throughout test suites to ensure consistent and
reliable setup of user and balance data, while allowing for easy dependency
mocking in different test scenarios.
"""

from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy import select

from authentication.user_management import check_user_has_token
from models.users import User, UserBalance
from tests.common.app_for_testing import testing_app as test_app
from tests.utils.mocks import mock_token_dependency
from tests.utils.test_data_setup import add_balances, add_users

USER_ID: int = 1
USER_BALANCE_ID: int = 1


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
    """
    Override application dependency for token validation during tests.

    This fixture replaces the `check_user_has_token` dependency with a mock
    implementation (`mock_token_dependency`) to simplify test scenarios that
    require token authentication. After the test executes, the dependency
    overrides are cleared to restore the default behavior.

    Yields:
        AsyncGenerator: Allows asynchronous tests to proceed with the mocked
            dependency.
    """
    test_app.dependency_overrides[check_user_has_token] = mock_token_dependency
    yield
    test_app.dependency_overrides = {}


@pytest_asyncio.fixture
async def initial_user_balance(async_db_session) -> UserBalance:
    """
    Retrieve the initial user balance from the database.

    This fixture queries the database to fetch the balance record for a
    specific user, identified by constants `USER_ID` and `USER_BALANCE_ID`.
    It is useful in scenarios where tests need access to the user's initial
    balance for assertions or updates.

    Args:
        async_db_session (AsyncSession): An active database session used
            for querying user balance data.

    Returns:
        UserBalance: The `UserBalance` object corresponding to the given
            user and balance IDs.
    """
    query = select(UserBalance).where(
        UserBalance.id == USER_BALANCE_ID,
        UserBalance.user_id == USER_ID,
    )
    user_balance = await async_db_session.execute(query)
    return user_balance.scalar_one()
