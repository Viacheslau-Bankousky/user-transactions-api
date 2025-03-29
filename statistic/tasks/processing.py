"""
Module for calculating and managing statistics for specified date ranges.

This module provides Celery tasks to calculate various user and transaction
statistics over specific date ranges. It uses Celery chords for parallel
task execution, ensuring efficient processing of multiple date ranges and their
aggregated results.

Key Features:
- **Date Range Statistics**: Calculates statistics for a single date range.
- **Bulk Range Statistics**: Calculates aggregated statistics across
  multiple date ranges.
- **Asynchronous Task Management**: Utilizes Celery tasks and chords for
  distributed task execution.

Dependencies:
- Celery for task orchestration.
- Custom statistic modules for processing user and transaction statistics.

Tasks:
- **calculate_statistics_for_date_range**: Calculates statistics for a
  given date range.
- **calculate_statistics_for_all_dates**: Calculates statistics for multiple
  date ranges and aggregates the results.
"""

from datetime import date
from typing import List, Tuple

from celery import chord

from core.celery_app import app
from statistic.tasks.responses import (
    create_final_statistic_response,
    create_statistic_response,
)
from statistic.tasks.transactions import (
    calculate_not_rollbacked_deposit_amount,
    calculate_not_rollbacked_transactions,
    calculate_not_rollbacked_withdraw_amount,
    calculate_transactions,
)
from statistic.tasks.users import (
    calculate_registered_and_deposit_users,
    calculate_registered_and_not_rollbacked_deposit_users,
    calculate_registered_users,
)


@app.task
def calculate_statistics_for_date_range(dt_gt: date, dt_lt: date) -> int:
    """
    Calculate statistics for a specific date range using Celery tasks.

    This task runs a group of parallel statistics calculations for a date
    range (`dt_gt` to `dt_lt`). Individual tasks include user statistics
    and transaction statistics. The results are then processed to create
    a single response for the date range.

    Args:
        dt_gt (date): Start date of the range.
        dt_lt (date): End date of the range.

    Returns:
        int: The task ID of the resulting chord.

    Workflow:
        1. Executes tasks to calculate:
            - Registered Users
            - Registered Users with Deposits
            - Registered and Non-Rollbacked Deposit Users
            - Transactions
            - Non-Rollbacked Transactions
            - Non-Rollbacked Deposit Amount
            - Non-Rollbacked Withdraw Amount
        2. Combines all results into a single response via
            `create_statistic_response`.

    Example:
        task_id = calculate_statistics_for_date_range(
        date(2023, 1, 1),
        date(2023, 1, 7)
        )
    """
    task_result = chord(
        [
            calculate_registered_users.s(dt_gt, dt_lt),
            calculate_registered_and_deposit_users.s(dt_gt, dt_lt),
            calculate_registered_and_not_rollbacked_deposit_users.s(
                dt_gt, dt_lt
            ),
            calculate_transactions.s(dt_gt, dt_lt),
            calculate_not_rollbacked_transactions.s(dt_gt, dt_lt),
            calculate_not_rollbacked_deposit_amount.s(dt_gt, dt_lt),
            calculate_not_rollbacked_withdraw_amount.s(dt_gt, dt_lt),
        ]
    )(create_statistic_response.s(dt_gt, dt_lt))

    return task_result.id


@app.task
def calculate_statistics_for_all_dates(
    date_ranges: List[Tuple[date, date]]
) -> int:
    """
    Calculate aggregated statistics for multiple date ranges.

    This task executes `calculate_statistics_for_date_range` for each
    date range in `date_ranges`. The results are aggregated into a final
    response using `create_final_statistic_response`.

    Args:
        date_ranges (List[Tuple[date, date]]): A list of date ranges,
            where each is a tuple of `(start_date, end_date)`.

    Returns:
        int: The task ID of the resulting aggregated response.

    Workflow:
        1. Executes `calculate_statistics_for_date_range` for each date range.
        2. Aggregates all results into a final response via
            `create_final_statistic_response`.

    Example:
        date_ranges = [
        (date(2023, 1, 1),
        date(2023, 1, 7)),
        (date(2023, 1, 8),
        date(2023, 1, 14))
        ]
        task_id = calculate_statistics_for_all_dates(date_ranges)
    """
    all_statistics_period = [
        calculate_statistics_for_date_range.s(dt_gt, dt_lt)
        for dt_gt, dt_lt in date_ranges
    ]
    statistic_result = chord(all_statistics_period)(
        create_final_statistic_response.s()
    )
    return statistic_result.id
