from datetime import date
from typing import Dict, List, Tuple

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
def calculate_statistics_for_date_range(
    dt_gt: date, dt_lt: date
) -> Dict[str, int | str]:
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
    all_statistics_period = [
        calculate_statistics_for_date_range.s(dt_gt, dt_lt)
        for dt_gt, dt_lt in date_ranges
    ]
    result = chord(all_statistics_period)(create_final_statistic_response.s())
    return result.id
