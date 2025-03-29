"""
Module for managing user balances.

This module provides a set of asynchronous functions to handle user
balance updates and queries in the context of transactions.
It utilizes SQLAlchemy's asynchronous ORM to interact with the
database and ensures atomic updates to user balances.

Key functionalities include:
- Retrieving the user's balance for a specific currency
 (`get_user_balance_for_currency`).
- Reducing a user's balance based on a transaction amount
 (`reduce_user_balance`).
- Restoring a user's balance for refund or withdrawal transactions
 (`restore_user_balance`).
- Increasing a user's balance based on a transaction amount
 (`increase_user_balance`).

This module is designed to ensure consistent and accurate balance
management while supporting various transaction purposes.
"""

from typing import Tuple

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from models.enums import TransactionPurposeEnum
from models.transactions import Transaction
from models.users import UserBalance


async def get_user_balance_for_currency(
    session: AsyncSession, user_id: int, currency: str
) -> UserBalance:
    """
    Retrieve a user's balance for a specific currency.

    Args:
        session (AsyncSession): The asynchronous SQLAlchemy session used
            to interact with the database.
        user_id (int): The ID of the user whose balance is being queried.
        currency (str): The currency code for which the balance is requested.

    Returns:
        UserBalance: The user's balance object for the specified currency.
    """
    query: Select[Tuple[UserBalance]] = select(UserBalance).where(
        (UserBalance.user_id == user_id) & (UserBalance.currency == currency)
    )
    user_balance: Result[Tuple[UserBalance]] = await session.execute(query)
    return user_balance.scalars().first()  # type: ignore


async def reduce_user_balance(
    session: AsyncSession, user_balance: UserBalance, transaction: Transaction
) -> None:
    """
    Reduce a user's balance by the specified transaction amount.

    Args:
        session (AsyncSession): The asynchronous SQLAlchemy session used
            to interact with the database.
        user_balance (UserBalance): The user's balance to be reduced.
        transaction (Transaction): The transaction object containing
            the amount to reduce from the balance.
    """
    user_balance.amount -= transaction.amount
    session.add(user_balance)
    await session.flush()


async def restore_user_balance(
    session: AsyncSession, user_balance: UserBalance, transaction: Transaction
) -> None:
    """
    Restore a user's balance based on the transaction's purpose.

    For a refund transaction, the amount is subtracted from the balance.
    For a withdrawal transaction, the amount is added back to the balance.

    Args:
        session (AsyncSession): The asynchronous SQLAlchemy session used
            to interact with the database.
        user_balance (UserBalance): The user's balance to be restored.
        transaction (Transaction): The transaction object containing the
            purpose and amount.
    """
    if transaction.purpose == TransactionPurposeEnum.REFUND:
        user_balance.amount -= transaction.amount
    elif transaction.purpose == TransactionPurposeEnum.WITHDRAWAL:
        user_balance.amount += transaction.amount

    session.add(user_balance)
    await session.flush()


async def increase_user_balance(
    session: AsyncSession, user_balance: UserBalance, transaction: Transaction
) -> None:
    """
    Increase a user's balance by the specified transaction amount.

    Args:
        session (AsyncSession): The asynchronous SQLAlchemy session
            used to interact with the database.
        user_balance (UserBalance): The user's balance to be increased.
        transaction (Transaction): The transaction object containing
            the amount to add to the balance.
    """
    user_balance.amount += transaction.amount
    session.add(user_balance)
    await session.flush()
