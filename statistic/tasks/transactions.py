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
from statistic.helpers import (  # format_metrics_response,; process_date_ranges_with_session,
    process_date_range_with_session,
    run_in_loop,
)

# @app.task
# def calculate_transactions(
#     date_ranges: List[Tuple[date, date]]
# ) -> List[Dict[str, str]]:
#     coro = process_date_ranges_with_session(
#         date_ranges=date_ranges,
#         metric_function=get_transactions_count,
#     )
#     results = run_in_loop(coro)
#     return format_metrics_response(
#         date_ranges=date_ranges,
#         metric_name="transactions_count",
#         metric_values=results,
#     )


@app.task
def calculate_transactions(dt_gt: date, dt_lt: date) -> Dict[str, int]:
    coro: Coroutine = process_date_range_with_session(
        dt_gt=dt_gt, dt_lt=dt_lt, metric_function=get_transactions_count
    )
    results: int = run_in_loop(coro)

    return {"transactions_count": results}


# @app.task
# def calculate_not_rollbacked_transactions(
#     date_ranges: List[Tuple[date, date]]
# ) -> List[Dict[str, str]]:
#     coro = process_date_ranges_with_session(
#         date_ranges=date_ranges,
#         metric_function=get_not_rollbacked_transactions_count,
#     )
#     results = run_in_loop(coro)
#     return format_metrics_response(
#         date_ranges=date_ranges,
#         metric_name="not_rollbacked_transactions_count",
#         metric_values=results,
#     )
@app.task
def calculate_not_rollbacked_transactions(
    dt_gt: date, dt_lt: date
) -> Dict[str, int]:
    coro: Coroutine = process_date_range_with_session(
        dt_gt=dt_gt,
        dt_lt=dt_lt,
        metric_function=get_not_rollbacked_transactions_count,
    )
    results: int = run_in_loop(coro)

    return {"not_rollbacked_transactions_count": results}


# @app.task
# def calculate_not_rollbacked_deposit_amount(
#     date_ranges: List[Tuple[date, date]]
# ) -> List[Dict[str, str]]:
#     coro = process_date_ranges_with_session(
#         date_ranges=date_ranges,
#         metric_function=get_not_rollbacked_transactions_amount,
#         transaction_purpose=TransactionPurposeEnum.REFUND,
#     )
#     results = run_in_loop(coro)
#     return format_metrics_response(
#         date_ranges=date_ranges,
#         metric_name="not_rollbacked_deposit_amount",
#         metric_values=results,
#     )


@app.task
def calculate_not_rollbacked_deposit_amount(
    dt_gt: date, dt_lt: date
) -> Dict[str, str]:
    coro: Coroutine = process_date_range_with_session(
        dt_gt=dt_gt,
        dt_lt=dt_lt,
        metric_function=get_not_rollbacked_transactions_amount,
        transaction_purpose=TransactionPurposeEnum.REFUND,
    )
    results: Decimal = run_in_loop(coro)

    return {"not_rollbacked_deposit_amount": str(results)}


# @app.task
# def calculate_not_rollbacked_withdraw_amount(
#     date_ranges: List[Tuple[date, date]]
# ) -> List[Dict[str, str]]:
#     coro = process_date_ranges_with_session(
#         date_ranges=date_ranges,
#         metric_function=get_not_rollbacked_transactions_amount,
#         transaction_purpose=TransactionPurposeEnum.WITHDRAWAL,
#     )
#     results = run_in_loop(coro)
#     return format_metrics_response(
#         date_ranges=date_ranges,
#         metric_name="not_rollbacked_withdraw_amount",
#         metric_values=results,
#     )


@app.task
def calculate_not_rollbacked_withdraw_amount(
    dt_gt: date, dt_lt: date
) -> Dict[str, str]:
    coro: Coroutine = process_date_range_with_session(
        dt_gt=dt_gt,
        dt_lt=dt_lt,
        metric_function=get_not_rollbacked_transactions_amount,
        transaction_purpose=TransactionPurposeEnum.WITHDRAWAL,
    )
    results: Decimal = run_in_loop(coro)

    return {"not_rollbacked_withdraw_amount": str(results)}
