"""
Module for Setting Up Transaction Test Data with Async Fixtures.

This module provides an asynchronous pytest fixture used for preparing
test data related to transactions and user balances. The fixture is
executed automatically before each test function, ensuring consistent
test setups.

Key Features:
- **Transaction Creation**: Adds a predefined set of transaction data
  to the database.
- **User Balance Updates**: Updates user account balances based on the
  generated transactions.

Dependencies:
- `pytest_asyncio`: For defining asynchronous pytest fixtures.
- `tests.utils.test_data_setup.add_transactions`: Function for adding
  transaction records to the session.
- `tests.utils.test_data_setup.update_user_balances`: Function for
 updating user account balances.

Examples:
This fixture is designed to be used in tests that involve database
transactions, ensuring all required data and balances are set up
prior to executing the tests.
"""

import pytest_asyncio

from tests.utils.test_data_setup import add_transactions, update_user_balances


@pytest_asyncio.fixture(scope="function", autouse=True)
async def transactions(async_db_session) -> None:
    """
    Prepare transaction data and update user balances before each test.

    This fixture adds transaction data to the database and updates user
    balances. It executes automatically before every test function due to
    `autouse=True`.

    Args:
        async_db_session (AsyncSession): An active asynchronous database
            session used for adding transactions and updating user balances.
    """
    await add_transactions(session=async_db_session)
    await update_user_balances(session=async_db_session)
