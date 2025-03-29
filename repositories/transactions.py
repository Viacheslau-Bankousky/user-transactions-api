"""
This module contains a set of functions for managing transactions in a db.

The module uses SQLAlchemy for database interactions and provides
a variety of utility functions to perform tasks such as retrieving
transactions, creating new transactions, performing rollbacks, and
obtaining aggregate statistics for transactions within specific
date ranges.

Key functionalities include:
- Creating a new transaction and saving it to the database
 (`create_transaction`).
- Fetching one or multiple transactions based on filtering criteria
 (`take_transaction`, `take_transactions`).
- Counting transactions in specific date ranges or filtering
 non-rollbacked ones (`get_transactions_count`,
  `get_not_rollbacked_transactions_count`).
- Calculating the total amount of non-rollbacked transactions for
 a specific purpose (`get_not_rollbacked_transactions_amount`).
- Rolling back a transaction by updating its status
 (`roll_back_transaction`).

The module heavily uses related models and helper methods,
 such as `Transaction`, `TransactionPurposeEnum`, and
 `TransactionStatusEnum`, alongside utility functions like
  `get_date_range_filter` and `prepare_filtered_query`.
"""

from datetime import date
from decimal import Decimal
from typing import List, Sequence, Tuple

from sqlalchemy import Result, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import BinaryExpression

from models.enums import TransactionPurposeEnum, TransactionStatusEnum
from models.transactions import Transaction
from repositories.query_builder import (
    get_date_range_filter,
    prepare_filtered_query,
)
from schemas.transactions import RequestTransactionModel


async def take_transactions(
    session: AsyncSession, **filter_params
) -> Sequence[Transaction]:
    """
    Retrieve multiple transactions from the db based on filtering criteria.

    Args:
        session (AsyncSession): An active async SQLAlchemy session.
        **filter_params (dict): Filtering parameters as key-value pairs
            to filter transactions.

    Returns:
        Sequence[Transaction]: A sequence of transaction objects matching
        the provided filters.
    """
    query: Select[Tuple[Transaction]] = prepare_filtered_query(
        model=Transaction, **filter_params
    )
    transactions: Result[Tuple[Transaction]] = await session.execute(query)
    return transactions.scalars().all()


async def create_transaction(
    session: AsyncSession,
    transaction_data: RequestTransactionModel,
    user_id: int,
) -> Transaction:
    """
    Create a new transaction in the database.

    Args:
        session (AsyncSession): An active async SQLAlchemy session.
        transaction_data (RequestTransactionModel): The data to populate
            the transaction.
        user_id (int): The ID of the user associated with this transaction.

    Returns:
        Transaction: The newly created transaction object.
    """
    transaction = Transaction(user_id=user_id, **transaction_data.model_dump())
    session.add(transaction)
    await session.flush()

    return transaction


async def take_transaction(
    session: AsyncSession, **filter_params
) -> Transaction | None:
    """
    Retrieve a single transaction based on filtering parameters.

    Args:
        session (AsyncSession): An active async SQLAlchemy session.
        **filter_params (dict): Filtering parameters as key-value pairs.

    Returns:
        Transaction | None: A single transaction object matching the filters,
        or `None` if no match is found.
    """
    query: Select[Tuple[Transaction]] = prepare_filtered_query(
        model=Transaction, **filter_params
    )
    transaction: Result[Tuple[Transaction]] = await session.execute(query)
    return transaction.scalars().first()


async def roll_back_transaction(
    session: AsyncSession,
    transaction: Transaction,
) -> Transaction:
    """
    Roll back an existing transaction by updating its status.

    Args:
        session (AsyncSession): An active async SQLAlchemy session.
        transaction (Transaction): The transaction to be rolled back.

    Returns:
        Transaction: The updated transaction object with its status
        set to ROLL_BACKED.
    """
    transaction.status = TransactionStatusEnum.ROLL_BACKED
    session.add(transaction)
    await session.flush()

    return transaction


async def get_transactions_count(
    session: AsyncSession, dt_gt: date, dt_lt: date
) -> int:
    """
    Get the count of transactions within a specified date range.

    Args:
        session (AsyncSession): An active async SQLAlchemy session.
        dt_gt (date): The start date of the date range.
        dt_lt (date): The end date of the date range.

    Returns:
        int: The number of transactions within the specified date range.
    """
    query: Select = select(func.count(Transaction.id)).where(
        get_date_range_filter(
            date_from=dt_gt, date_to=dt_lt, model=Transaction
        )
    )
    transactions_result: Result = await session.execute(query)
    transactions_count: int = transactions_result.scalar()
    return transactions_count


async def get_not_rollbacked_transactions_count(
    session: AsyncSession, dt_gt: date, dt_lt: date
) -> int:
    """
    Get the count of transactions within a specific date range.

    Only transactions that are not marked as rollbacked are counted.

    Args:
        session (AsyncSession): An active async SQLAlchemy session.
        dt_gt (date): The start date of the date range.
        dt_lt (date): The end date of the date range.

    Returns:
        int: The number of non-rollbacked transactions within the specified
        date range.
    """
    query: Select = select(func.count(Transaction.id)).where(
        get_date_range_filter(
            date_from=dt_gt, date_to=dt_lt, model=Transaction
        ),
        Transaction.status != TransactionStatusEnum.ROLL_BACKED,
    )
    transactions_result: Result = await session.execute(query)
    transactions_count: int = transactions_result.scalar()
    return transactions_count


async def get_not_rollbacked_transactions_amount(
    session: AsyncSession,
    dt_gt: date,
    dt_lt: date,
    transaction_purpose: TransactionPurposeEnum,
) -> Decimal:
    """
    Calculate the total amount of non-rollbacked transactions.

    Args:
        session (AsyncSession): An active async SQLAlchemy session.
        dt_gt (date): The start date of the date range.
        dt_lt (date): The end date of the date range.
        transaction_purpose (TransactionPurposeEnum): The purpose of the
            transaction (e.g., REFUND, WITHDRAWAL).

    Returns:
        Decimal: The total amount of matching transactions.
        Returns `0` if no matches are found.
    """
    conditions: List[BinaryExpression] = [
        get_date_range_filter(
            date_from=dt_gt, date_to=dt_lt, model=Transaction
        ),
        Transaction.status != TransactionStatusEnum.ROLL_BACKED,
    ]
    if transaction_purpose == TransactionPurposeEnum.REFUND:
        conditions.append(Transaction.purpose == transaction_purpose)
    elif transaction_purpose == TransactionPurposeEnum.WITHDRAWAL:
        conditions.append(Transaction.purpose == transaction_purpose)

    query: Select = select(func.sum(Transaction.amount)).where(*conditions)
    transactions_result: Result = await session.execute(query)
    transactions_amount: Decimal | None = transactions_result.scalar()
    return transactions_amount if transactions_amount else Decimal(0)
