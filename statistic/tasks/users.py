"""
Module for calculating user statistics.

This module provides Celery tasks to calculate various user-related
statistics for given date ranges. These include the total number of
registered users, users with deposits within a specified time range,
and users with non-rollbacked deposits.

Key Features:
- **User Counts**: Calculates the total number of registered users
 and registered users with deposit transactions.
- **Non-Rollbacked Deposits**: Calculates the number of users with
 deposits that were not rolled back.

Dependencies:
- Requires Celery for task orchestration.
- Utilizes repository functions for retrieving user statistics.

Tasks:
- **calculate_registered_users**: Calculates the total number
 of registered users.
- **calculate_registered_and_deposit_users**: Calculates the
 total number of registered users with deposits.
- **calculate_registered_and_not_rollbacked_deposit_users**:
 Calculates the total number of registered users with
 non-rollbacked deposits.
"""

from datetime import date
from typing import Coroutine, Dict

from core.celery_app import app
from repositories.users import (
    get_registered_users_count,
    get_users_count_with_deposit_transactions,
)
from statistic.helpers import (
    process_date_range_with_session,
    run_in_loop,
)


@app.task
def calculate_registered_users(dt_gt: date, dt_lt: date) -> Dict[str, int]:
    """
    Calculate the total number of users registered in a given date range.

    Args:
        dt_gt (date): Start date of the range.
        dt_lt (date): End date of the range.

    Returns:
        Dict[str, int]: A dictionary containing the count of registered
            users.
    """
    coro: Coroutine = process_date_range_with_session(
        dt_gt=dt_gt, dt_lt=dt_lt, metric_function=get_registered_users_count
    )
    metric_result: int = run_in_loop(coro)

    return {"registered_users_count": metric_result}


@app.task
def calculate_registered_and_deposit_users(
    dt_gt: date, dt_lt: date
) -> Dict[str, int]:
    """
    Calculate the total number of registered users who made deposits.

    Args:
        dt_gt (date): Start date of the range.
        dt_lt (date): End date of the range.

    Returns:
        Dict[str, int]: A dictionary containing the count of registered
            in a given date range users who made deposits.
    """
    coro: Coroutine = process_date_range_with_session(
        dt_gt=dt_gt,
        dt_lt=dt_lt,
        metric_function=get_users_count_with_deposit_transactions,
    )
    metric_result: int = run_in_loop(coro)

    return {"registered_and_deposit_users_count": metric_result}


@app.task
def calculate_registered_and_not_rollbacked_deposit_users(
    dt_gt: date, dt_lt: date
) -> Dict[str, int]:
    """
    Calculate the total number of registered users who made deposits.

    Here we assume that a deposit is not rollbacked

    Args:
        dt_gt (date): Start date of the range.
        dt_lt (date): End date of the range.

    Returns:
        Dict[str, int]: A dictionary containing the count of registered
            in a given date range users who made deposits that were not
            rollbacked.
    """
    coro: Coroutine = process_date_range_with_session(
        dt_gt=dt_gt,
        dt_lt=dt_lt,
        metric_function=get_users_count_with_deposit_transactions,
    )
    metric_result: int = run_in_loop(coro)

    return {"registered_and_not_rollbacked_deposit_users_count": metric_result}
