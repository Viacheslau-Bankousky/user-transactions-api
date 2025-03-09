from datetime import date
from typing import Dict, List, Tuple

from repositories.users import (
    get_registered_users_count,
    get_users_count_with_filters,
)
from statistic.celery_app import app
from statistic.helpers import format_metrics_response, run_in_loop
from statistic.metrics_processing import process_date_ranges_with_session


@app.task
def calculate_registered_users(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    async def _calculate():
        results = await process_date_ranges_with_session(
            date_ranges=date_ranges, metric_function=get_registered_users_count
        )
        return format_metrics_response(
            date_ranges=date_ranges,
            metric_name="registered_users_count",
            metric_values=results,
        )

    return run_in_loop(_calculate())


@app.task
def calculate_registered_and_deposit_users(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    async def _calculate():
        results = await process_date_ranges_with_session(
            date_ranges=date_ranges,
            metric_function=get_users_count_with_filters,
        )
        return format_metrics_response(
            date_ranges=date_ranges,
            metric_name="registered_and_deposit_users_count",
            metric_values=results,
        )

    return run_in_loop(_calculate())


@app.task
def calculate_registered_and_not_rollbacked_deposit_users(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    async def _calculate():
        results = await process_date_ranges_with_session(
            date_ranges=date_ranges,
            metric_function=get_users_count_with_filters,
            exclude_rollbacked=True,
        )
        return format_metrics_response(
            date_ranges=date_ranges,
            metric_name="registered_and_not_rollbacked_deposit_users_count",
            metric_values=results,
        )

    return run_in_loop(_calculate())
