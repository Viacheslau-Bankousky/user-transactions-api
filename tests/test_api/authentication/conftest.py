"""
Module for Adding Async Fixtures to setup Test User Data.

This module contains an asynchronous pytest fixture designed for
test setups that require the creation of a specific user in
the database. It simplifies test preparation by ensuring the
required user exists in the database before each test function.

Key Features:
- **Predefined User:** Automatically creates a user with a hashed
 password before each test.
- **Automatic Execution:** Executes before each test function due to
  `autouse=True`, ensuring consistency in test environments.

Dependencies:
- `pytest_asyncio`: For defining asynchronous pytest fixtures.
- `authentication.security.get_password_hash`: A utility for hashing
 user passwords.
- `models.users.User`: The SQLAlchemy user model representing user data.

Examples:
This fixture is used in test cases that require a predefined user, such
as tests involving authentication, user lookup, or related database
 operations.
"""

import pytest_asyncio

from authentication.security import get_password_hash
from models.users import User


@pytest_asyncio.fixture(scope="function", autouse=True)
async def user(async_db_session) -> None:
    """
    Add a predefined test user to the database.

    This fixture creates and adds a user with a hashed password
    to the database before each test function.
    The user has a predefined name, email, and password.
    The `autouse=True` parameter ensures that this setup is
    automatically applied to every test function in the scope.

    Args:
        async_db_session (AsyncSession): An active asynchronous
            database session used for adding the user to the database.

    Example:
        This user will automatically be available for any test case.
    """
    user = User(
        name="fourth_user",
        email="fourth@user.com",
        password=get_password_hash("<PASSWORD4>"),
    )
    async_db_session.add(user)
    await async_db_session.flush()
