from datetime import date
from typing import Dict, List, Tuple

from core.celery_app import app
from repositories.users import (
    get_registered_users_count,
    get_users_count_with_filters,
)
from statistic.helpers import (
    format_metrics_response,
    process_date_ranges_with_session,
    run_in_loop,
)


@app.task
def calculate_registered_users(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    coro = process_date_ranges_with_session(
        date_ranges=date_ranges, metric_function=get_registered_users_count
    )
    results = run_in_loop(coro)
    return format_metrics_response(
        date_ranges=date_ranges,
        metric_name="registered_users_count",
        metric_values=results,
    )


@app.task
def calculate_registered_and_deposit_users(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    coro = process_date_ranges_with_session(
        date_ranges=date_ranges, metric_function=get_users_count_with_filters
    )
    results = run_in_loop(coro)
    return format_metrics_response(
        date_ranges=date_ranges,
        metric_name="registered_and_deposit_users_count",
        metric_values=results,
    )


@app.task
def calculate_registered_and_not_rollbacked_deposit_users(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    coro = process_date_ranges_with_session(
        date_ranges=date_ranges,
        metric_function=get_users_count_with_filters,
        exclude_rollbacked=True,
    )
    results = run_in_loop(coro)
    return format_metrics_response(
        date_ranges=date_ranges,
        metric_name="registered_and_not_rollbacked_deposit_users_count",
        metric_values=results,
    )
