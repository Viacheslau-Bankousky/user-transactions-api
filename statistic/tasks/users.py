from datetime import date
from typing import Coroutine, Dict

from core.celery_app import app
from repositories.users import (
    get_registered_users_count,
    get_users_count_with_filters,
)
from statistic.helpers import (
    process_date_range_with_session,
    run_in_loop,
)


@app.task
def calculate_registered_users(
    dt_gt: date, dt_lt: date
) -> Dict[str, int]:
    coro: Coroutine = process_date_range_with_session(
        dt_gt=dt_gt, dt_lt=dt_lt, metric_function=get_registered_users_count
    )
    results: int = run_in_loop(coro)

    return {"registered_users_count": results}


@app.task
def calculate_registered_and_deposit_users(
    dt_gt: date, dt_lt: date
) -> Dict[str, int]:
    coro: Coroutine = process_date_range_with_session(
        dt_gt=dt_gt, dt_lt=dt_lt, metric_function=get_users_count_with_filters
    )
    results: int = run_in_loop(coro)

    return {"registered_and_deposit_users_count": results}


@app.task
def calculate_registered_and_not_rollbacked_deposit_users(
    dt_gt: date, dt_lt: date
) -> Dict[str, int]:
    coro: Coroutine = process_date_range_with_session(
        dt_gt=dt_gt,
        dt_lt=dt_lt,
        metric_function=get_users_count_with_filters,
    )
    results: int = run_in_loop(coro)

    return {"registered_and_not_rollbacked_deposit_users_count": results}
