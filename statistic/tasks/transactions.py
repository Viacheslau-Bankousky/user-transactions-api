from datetime import date
from typing import Dict, List, Tuple

from core.celery_app import app
from models.enums import TransactionPurposeEnum
from repositories.transactions import (
    get_not_rollbacked_transactions_amount,
    get_not_rollbacked_transactions_count,
    get_transactions_count,
)
from statistic.helpers import (
    format_metrics_response,
    process_date_ranges_with_session,
    run_in_loop,
)


@app.task
def calculate_transactions(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    coro = process_date_ranges_with_session(
        date_ranges=date_ranges,
        metric_function=get_transactions_count,
    )
    results = run_in_loop(coro)
    return format_metrics_response(
        date_ranges=date_ranges,
        metric_name="transactions_count",
        metric_values=results,
    )


@app.task
def calculate_not_rollbacked_transactions(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    coro = process_date_ranges_with_session(
        date_ranges=date_ranges,
        metric_function=get_not_rollbacked_transactions_count,
    )
    results = run_in_loop(coro)
    return format_metrics_response(
        date_ranges=date_ranges,
        metric_name="not_rollbacked_transactions_count",
        metric_values=results,
    )


@app.task
def calculate_not_rollbacked_deposit_amount(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    coro = process_date_ranges_with_session(
        date_ranges=date_ranges,
        metric_function=get_not_rollbacked_transactions_amount,
        transaction_purpose=TransactionPurposeEnum.REFUND,
    )
    results = run_in_loop(coro)
    return format_metrics_response(
        date_ranges=date_ranges,
        metric_name="not_rollbacked_deposit_amount",
        metric_values=results,
    )


@app.task
def calculate_not_rollbacked_withdraw_amount(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    coro = process_date_ranges_with_session(
        date_ranges=date_ranges,
        metric_function=get_not_rollbacked_transactions_amount,
        transaction_purpose=TransactionPurposeEnum.WITHDRAWAL,
    )
    results = run_in_loop(coro)
    return format_metrics_response(
        date_ranges=date_ranges,
        metric_name="not_rollbacked_withdraw_amount",
        metric_values=results,
    )
