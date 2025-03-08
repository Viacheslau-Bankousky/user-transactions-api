import asyncio
from datetime import date
from decimal import Decimal
from typing import Dict, List, Tuple

from core.database import get_session
from models.enums import TransactionPurposeEnum
from repositories.transactions import (
    get_not_rollbacked_transactions_amount,
    get_not_rollbacked_transactions_count,
    get_transactions_count,
)
from statistic.celery_app import app
from statistic.helpers import format_metrics_response

# @app.task
# def calculate_transactions(dt_gt: date, dt_lt: date) -> Dict[str, int]:
#     async def _calculate_inner():
#         async with get_session() as session:
#             transactions_count: int = await get_transactions_count(
#                 session=session, dt_gt=dt_gt, dt_lt=dt_lt
#             )
#             return {"transactions_count": transactions_count}
#
#     return asyncio.run(_calculate_inner())


@app.task
def calculate_transactions(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    async def _calculate_inner() -> List[Dict[str, str]]:
        coroutines: List = []
        async with get_session() as session:
            for date_range in date_ranges:
                dt_gt, dt_lt = date_range
                coroutines.append(
                    get_transactions_count(
                        session=session, dt_gt=dt_gt, dt_lt=dt_lt
                    )
                )

            transactions_count_values: List[int] = await asyncio.gather(
                *coroutines
            )
            return format_metrics_response(
                date_range=date_range,
                metric_name="transactions_count",
                metric_values=transactions_count_values,
            )

    return asyncio.run(_calculate_inner())


# @app.task
# def calculate_not_rollbacked_transactions(dt_gt: date, dt_lt: date) -> Dict[str, int]:
#     async def _calculate_inner():
#         async with get_session() as session:
#             transactions_count: int = await get_not_rollbacked_transactions_count(
#                 session=session, dt_gt=dt_gt, dt_lt=dt_lt
#             )
#             return {"not_rollbacked_transactions_count": transactions_count}
#
#     return asyncio.run(_calculate_inner())


@app.task
def calculate_not_rollbacked_transactions(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    async def _calculate_inner() -> List[Dict[str, str]]:
        coroutines: List = []
        async with get_session() as session:
            for date_range in date_ranges:
                dt_gt, dt_lt = date_range
                coroutines.append(
                    get_not_rollbacked_transactions_count(
                        session=session, dt_gt=dt_gt, dt_lt=dt_lt
                    )
                )

            transactions_count_values: List[int] = await asyncio.gather(
                *coroutines
            )
            return format_metrics_response(
                date_range=date_range,
                metric_name="not_rollbacked_transactions_count",
                metric_values=transactions_count_values,
            )

    return asyncio.run(_calculate_inner())


# @app.task
# def calculate_not_rollbacked_deposit_amount(
#     dt_gt: date, dt_lt: date
# ) -> Dict[str, str]:
#     async def _calculate_inner():
#         async with get_session() as session:
#             deposit_amount: Decimal = (
#                 await get_not_rollbacked_transactions_amount(
#                     session=session,
#                     dt_gt=dt_gt,
#                     dt_lt=dt_lt,
#                     transaction_purpose=TransactionPurposeEnum.REFUND,
#                 )
#             )
#             return {"not_rollbacked_deposit_amount": str(deposit_amount)}
#
#     return asyncio.run(_calculate_inner())


@app.task
def calculate_not_rollbacked_deposit_amount(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    async def _calculate_inner() -> List[Dict[str, str]]:
        coroutines: List = []
        async with get_session() as session:
            for date_range in date_ranges:
                dt_gt, dt_lt = date_range
                coroutines.append(
                    get_not_rollbacked_transactions_amount(
                        session=session,
                        dt_gt=dt_gt,
                        dt_lt=dt_lt,
                        transaction_purpose=TransactionPurposeEnum.REFUND,
                    )
                )
            deposit_amount_values: List[Decimal] = await asyncio.gather(
                *coroutines
            )
            return format_metrics_response(
                date_range=date_range,
                metric_name="not_rollbacked_deposit_amount",
                metric_values=deposit_amount_values,
            )

    return asyncio.run(_calculate_inner())


# @app.task
# def calculate_not_rollbacked_withdraw_amount(
#     dt_gt: date, dt_lt: date
# ) -> Dict[str, str]:
#     async def _calculate_inner():
#         async with get_session() as session:
#             deposit_amount: Decimal = (
#                 await get_not_rollbacked_transactions_amount(
#                     session=session,
#                     dt_gt=dt_gt,
#                     dt_lt=dt_lt,
#                     transaction_purpose=TransactionPurposeEnum.WITHDRAWAL,
#                 )
#             )
#             return {"not_rollbacked_withdraw_amount": str(deposit_amount)}
#
#     return asyncio.run(_calculate_inner())


@app.task
def calculate_not_rollbacked_withdraw_amount(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    async def _calculate_inner() -> List[Dict[str, str]]:
        coroutines: List = []
        async with get_session() as session:
            for date_range in date_ranges:
                dt_gt, dt_lt = date_range
                coroutines.append(
                    get_not_rollbacked_transactions_amount(
                        session=session,
                        dt_gt=dt_gt,
                        dt_lt=dt_lt,
                        transaction_purpose=TransactionPurposeEnum.WITHDRAWAL,
                    )
                )
            withdraw_amount_values: List[Decimal] = await asyncio.gather(
                *coroutines
            )
            return format_metrics_response(
                date_range=date_range,
                metric_name="not_rollbacked_withdraw_amount",
                metric_values=withdraw_amount_values,
            )

    return asyncio.run(_calculate_inner())
