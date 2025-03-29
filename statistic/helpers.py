"""
Utility functions for miscellaneous tasks.

This module provides utility functions for working with date ranges,
running asynchronous tasks in synchronous contexts, and processing
database-related operations with sessions over specified date ranges.

Key Features:
- **Date Range Generation**: Generates date ranges for given weeks.
- **Async to Sync Execution**: Executes asynchronous coroutines
 in synchronous contexts.
- **Database Session Handling**: Processes date ranges with
 database sessions.

Dependencies:
- Utilizes `asyncio` for event loop operations.
- Requires `get_session` for database session management.

Functions:
- **generate_date_ranges**: Generates weekly date ranges going
 backward from the current date, up to the specified number of weeks.
- **run_in_loop**: Executes a coroutine in a synchronous blocking way.
- **process_date_range_with_session**: Processes operations over a given
 date range with database session handling.
"""

import asyncio
from datetime import date, timedelta
from typing import Any, Awaitable, Callable, List, Tuple

from core.database import get_session


def generate_date_ranges(weeks_count: int) -> List[Tuple[date, date]]:
    """
    Generate a list of weekly date ranges.

    Args:
        weeks_count (int): The number of weeks to generate date ranges for.

    Returns:
        List[Tuple[date, date]]: A list of tuples, where each tuple contains
            the start and end dates (inclusive) of a week.

    Example:
        If today is 2023-12-15 and weeks_count is 2, the output will be:
        [(2023-12-01, 2023-12-07), (2023-12-08, 2023-12-14)]
    """
    date_ranges: List = []
    start_date: date = date.today() - timedelta(weeks=weeks_count)
    dt_gt: date = start_date
    dt_lt: date = start_date + timedelta(days=6)
    while dt_lt <= date.today():
        date_ranges.append((dt_gt, dt_lt))
        dt_gt += timedelta(days=7)
        dt_lt += timedelta(days=7)

    date_ranges.reverse()
    return date_ranges


def run_in_loop(coro: Awaitable[Any]) -> Any:
    """
    Execute an asynchronous coroutine in a synchronous context.

    Args:
        coro (Awaitable[Any]): The coroutine to execute.

    Returns:
        Any: The result of the coroutine execution.

    Notes:
        - If there is no running event loop, a new one is created and set.
        - If `RuntimeError` is raised (e.g., in non-async contexts), a new
            event loop is managed internally.
    """
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)


async def process_date_range_with_session(
    dt_gt: date,
    dt_lt: date,
    metric_function: Callable,
    **kwargs,
) -> List[Any]:
    """
    Process operations over a given date range with an asynchronous db session.

    Args:
        dt_gt (date): The start date of the range (greater than or equal to).
        dt_lt (date): The end date of the range (less than or equal to).
        metric_function (Callable): An async function to process the range.
            The `metric_function` must accept at least three arguments:
            `session` (AsyncSession), `dt_gt` (start date), and `dt_lt`
            (end date).
        **kwargs: Additional keyword arguments to pass to `metric_function`.

    Returns:
        List[Any]: The result of the `metric_function` execution.

    Example:
        async def my_metric_function(session, dt_gt, dt_lt, **kwargs):
            # Perform operations
            return results

        results = await process_date_range_with_session(
            dt_gt=some_start_date,
            dt_lt=some_end_date,
            metric_function=my_metric_function,
            extra_arg="value",
        )
    """
    async with get_session() as session:
        return await metric_function(session, dt_gt, dt_lt, **kwargs)
