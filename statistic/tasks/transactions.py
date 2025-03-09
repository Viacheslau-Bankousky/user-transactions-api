from datetime import date
from typing import Dict, List, Tuple

from models.enums import TransactionPurposeEnum
from repositories.transactions import (
    get_not_rollbacked_transactions_amount,
    get_not_rollbacked_transactions_count,
    get_transactions_count,
)
from statistic.celery_app import app
from statistic.helpers import format_metrics_response, run_in_loop
from statistic.metrics_processing import process_date_ranges_with_session


@app.task
def calculate_transactions(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    async def _calculate():
        results = await process_date_ranges_with_session(
            date_ranges=date_ranges,
            metric_function=get_transactions_count,
        )
        return format_metrics_response(
            date_ranges=date_ranges,
            metric_name="transactions_count",
            metric_values=results,
        )

    return run_in_loop(_calculate())


@app.task
def calculate_not_rollbacked_transactions(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    async def _calculate():
        results = await process_date_ranges_with_session(
            date_ranges=date_ranges,
            metric_function=get_not_rollbacked_transactions_count,
        )
        return format_metrics_response(
            date_ranges=date_ranges,
            metric_name="not_rollbacked_transactions_count",
            metric_values=results,
        )

    return run_in_loop(_calculate())


@app.task
def calculate_not_rollbacked_deposit_amount(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    async def _calculate():
        results = await process_date_ranges_with_session(
            date_ranges=date_ranges,
            metric_function=get_not_rollbacked_transactions_amount,
            transaction_purpose=TransactionPurposeEnum.REFUND,
        )
        return format_metrics_response(
            date_ranges=date_ranges,
            metric_name="not_rollbacked_deposit_amount",
            metric_values=results,
        )

    return run_in_loop(_calculate())


@app.task
def calculate_not_rollbacked_withdraw_amount(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    async def _calculate():
        results = await process_date_ranges_with_session(
            date_ranges=date_ranges,
            metric_function=get_not_rollbacked_transactions_amount,
            transaction_purpose=TransactionPurposeEnum.WITHDRAWAL,
        )
        return format_metrics_response(
            date_ranges=date_ranges,
            metric_name="not_rollbacked_withdraw_amount",
            metric_values=results,
        )

    return run_in_loop(_calculate())
