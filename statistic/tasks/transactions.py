"""
Module for calculating transaction statistics.

This module provides Celery tasks to calculate various transaction-related
statistics for a given date range. These include the total number of
transactions, the count of non-rollbacked transactions, as well as the
amounts for non-rollbacked deposits and withdrawals.

Key Features:
- **Transaction Counts**: Calculates the total number of transactions
  as well as non-rollbacked transactions.
- **Transaction Amounts**: Calculates amounts for non-rollbacked deposits
  and withdrawals.
- **Async Execution**: Uses utility functions to process data asynchronously
  with database sessions.

Dependencies:
- Requires Celery for task orchestration.
- Utilizes repository functions for transaction statistics retrieval.

Tasks:
- **calculate_transactions**: Calculates the total number of transactions.
- **calculate_not_rollbacked_transactions**: Calculates the count of
  non-rollbacked transactions.
- **calculate_not_rollbacked_deposit_amount**: Calculates the amount for
  non-rollbacked deposits.
- **calculate_not_rollbacked_withdraw_amount**: Calculates the amount for
  non-rollbacked withdrawals.
"""

from datetime import date
from decimal import Decimal
from typing import Coroutine, Dict

from core.celery_app import app
from models.enums import TransactionPurposeEnum
from repositories.transactions import (
    get_not_rollbacked_transactions_amount,
    get_not_rollbacked_transactions_count,
    get_transactions_count,
)
from statistic.helpers import (
    process_date_range_with_session,
    run_in_loop,
)


@app.task
def calculate_transactions(dt_gt: date, dt_lt: date) -> Dict[str, int]:
    """
    Calculate the total number of transactions in a given date range.

    Args:
        dt_gt (date): Start date of the range.
        dt_lt (date): End date of the range.

    Returns:
        Dict[str, int]: A dictionary containing the total transaction
            count.
    """
    coro: Coroutine = process_date_range_with_session(
        dt_gt=dt_gt, dt_lt=dt_lt, metric_function=get_transactions_count
    )
    metric_result: int = run_in_loop(coro)

    return {"transactions_count": metric_result}


@app.task
def calculate_not_rollbacked_transactions(
    dt_gt: date, dt_lt: date
) -> Dict[str, int]:
    """
    Calculate the count of non-rollbacked transactions.

    Args:
        dt_gt (date): Start date of the range.
        dt_lt (date): End date of the range.

    Returns:
        Dict[str, int]: A dictionary containing the count
            of non-rollbacked transactions in the given
            date range.
    """
    coro: Coroutine = process_date_range_with_session(
        dt_gt=dt_gt,
        dt_lt=dt_lt,
        metric_function=get_not_rollbacked_transactions_count,
    )
    metric_result: int = run_in_loop(coro)

    return {"not_rollbacked_transactions_count": metric_result}


@app.task
def calculate_not_rollbacked_deposit_amount(
    dt_gt: date, dt_lt: date
) -> Dict[str, str]:
    """
    Calculate the total amount of non-rollbacked deposits.

    Args:
        dt_gt (date): Start date of the range.
        dt_lt (date): End date of the range.

    Returns:
        Dict[str, str]: A dictionary containing the total amount
            of non-rollbacked deposits (as a string) in the given
            date range.
    """
    coro: Coroutine = process_date_range_with_session(
        dt_gt=dt_gt,
        dt_lt=dt_lt,
        metric_function=get_not_rollbacked_transactions_amount,
        transaction_purpose=TransactionPurposeEnum.REFUND,
    )
    metric_result: Decimal = run_in_loop(coro)

    return {"not_rollbacked_deposit_amount": str(metric_result)}


@app.task
def calculate_not_rollbacked_withdraw_amount(
    dt_gt: date, dt_lt: date
) -> Dict[str, str]:
    """
    Calculate the total amount of non-rollbacked withdrawals.

    Args:
        dt_gt (date): Start date of the range.
        dt_lt (date): End date of the range.

    Returns:
        Dict[str, str]: A dictionary containing the total amount
            of non-rollbacked withdrawals (as a string) in a given
            date range.
    """
    coro: Coroutine = process_date_range_with_session(
        dt_gt=dt_gt,
        dt_lt=dt_lt,
        metric_function=get_not_rollbacked_transactions_amount,
        transaction_purpose=TransactionPurposeEnum.WITHDRAWAL,
    )
    metric_result: Decimal = run_in_loop(coro)

    return {"not_rollbacked_withdraw_amount": str(metric_result)}
