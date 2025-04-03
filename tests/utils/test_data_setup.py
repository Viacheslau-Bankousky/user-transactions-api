"""
Database Utility Module for User and Transaction Management.

This module provides a set of asynchronous functions for managing users,
balances, and transactions in a database. It is designed for use with
SQLAlchemy and an asynchronous database session. These utilities simplify
operations required for setting up test data or managing database
interactions in the application.

Key Features:
- **User Management**: Add users to the database with varying attributes.
- **Balance Management**: Initialize user balances for multiple currencies.
- **Transaction Management**: Add transaction records to the database.
- **Balance Updates**: Adjust balances in response to specific operations.

Dependencies:
- `SQLAlchemy`: For asynchronous database session (`AsyncSession`).
- `models.enums.CurrencyEnum`: Enum for supported currencies.
- `models.enums.TransactionPurposeEnum`: Enum specifying transaction purposes.
- `models.users`: Contains the definitions for `User` and `UserBalance` models.
- `models.transactions`: Contains the definition for the `Transaction` model.
- `repositories.users_balances.get_user_balance_for_currency`: Helper function
  for querying user balances by currency.
- `schemas.users.UserStatusEnum`: Enum for user status values.

Constants:
- **REFUND_TRANSACTION_AMOUNT**: A predefined transaction refund amount
 (`Decimal`).
- **USER_ID**: A user identifier for test or example cases.
- **BLOCKED_USER_ID**: A user identifier for blocked accounts.

Examples:
These utility functions are typically used for seeding test data or performing
core database operations related to user balances and transactions.
"""

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from models.enums import CurrencyEnum, TransactionPurposeEnum
from models.transactions import Transaction
from models.users import User, UserBalance
from repositories.users_balances import get_user_balance_for_currency
from schemas.users import UserStatusEnum

REFUND_TRANSACTION_AMOUNT: Decimal = Decimal(1000)
USER_ID: int = 1
BLOCKED_USER_ID: int = 3


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
        User(
            name="first_user", email="first@user.com", password="<PASSWORD1>"
        ),
        User(
            name="second_user", email="second@user.com", password="<PASSWORD2>"
        ),
        User(
            name="third_user",
            email="third@user.com",
            password="<PASSWORD3>",
            status=UserStatusEnum.BLOCKED,
        ),
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


async def add_transactions(session: AsyncSession) -> None:
    """
    Create and add transaction records to the database.

    This function adds a predefined set of transactions to the database.
    The transactions include a refund for a specific user and another for
    a blocked user.

    Args:
        session (AsyncSession): The SQLAlchemy asynchronous session used for
            database operations.
    """
    transactions = [
        Transaction(
            user_id=USER_ID,
            currency=CurrencyEnum.USD,
            amount=REFUND_TRANSACTION_AMOUNT,
            purpose=TransactionPurposeEnum.REFUND,
        ),
        Transaction(
            user_id=BLOCKED_USER_ID,
            currency=CurrencyEnum.USD,
            amount=REFUND_TRANSACTION_AMOUNT,
            purpose=TransactionPurposeEnum.REFUND,
        ),
    ]

    session.add_all(transactions)
    await session.flush()


async def update_user_balances(session: AsyncSession) -> None:
    """
    Update the balance for a specific user and currency.

    This function retrieves the balance record for a given user and
    currency, increments it by a predefined refund amount, and updates
    the database.

    Args:
        session (AsyncSession): The SQLAlchemy asynchronous session used
            for database operations.
    """
    user_balance: UserBalance = await get_user_balance_for_currency(
        session=session, user_id=USER_ID, currency=CurrencyEnum.USD
    )
    user_balance.amount += REFUND_TRANSACTION_AMOUNT
    session.add(user_balance)
    await session.flush()
