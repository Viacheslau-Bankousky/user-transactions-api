"""
Module for managing user and balance data in the database.

This module provides asynchronous utility functions to create and add users
and their associated balance data to the database. It relies on SQLAlchemy's
asynchronous session to perform database operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from models.enums import CurrencyEnum
from models.users import User, UserBalance


async def add_users(session: AsyncSession) -> list[User]:
    """
    Create and add users to the database.

    Args:
        session (AsyncSession): The SQLAlchemy asynchronous session used
            for database operations.

    Returns:
        list[User]: A list of created User objects that were added to the
            database.
    """
    user_list = [
        User(name="first_user", email="first@user.com"),
        User(name="last_user", email="last@user.com"),
    ]
    session.add_all(user_list)
    await session.flush()
    return user_list


async def add_balances(session: AsyncSession, users: list[User]) -> None:
    """
    Create and add user balance data for each user.

    Args:
        session (AsyncSession): The SQLAlchemy asynchronous session used
            for database operations.
        users (list[User]): A list of User objects for whom the balance
            data will be created and added.
    """
    balances: list[UserBalance] = []
    for user in users:
        balances.extend(
            UserBalance(user_id=user.id, currency=currency)
            for currency in CurrencyEnum
        )
    session.add_all(balances)
    await session.commit()
