import asyncio
from datetime import date
from typing import Dict, List, Tuple

from core.database import get_session
from repositories.users import (
    get_registered_users_count,
    get_users_count_with_filters,
)
from statistic.celery_app import app
from statistic.helpers import format_metrics_response

# @app.task
# def calculate_registered_users(dt_gt: date, dt_lt: date)-> List[Dict[str, str]]:
#     async def _calculate_inner():
#         async with get_session() as session:
#             users_count: int = await get_registered_users_count(
#                 session=session, dt_gt=dt_gt, dt_lt=dt_lt
#             )
#             return {"registered_users_count": users_count}
#
#     return asyncio.run(_calculate_inner())


@app.task
def calculate_registered_users(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    async def _calculate_inner():
        coroutines: List = []
        async with get_session() as session:
            for date_range in date_ranges:
                dt_gt, dt_lt = date_range
                coroutines.append(
                    get_registered_users_count(
                        session=session, dt_gt=dt_gt, dt_lt=dt_lt
                    )
                )

            users_count_values: List[int] = await asyncio.gather(*coroutines)
            return format_metrics_response(
                date_range=date_range,
                metric_name="registered_users_count",
                metric_values=users_count_values,
            )

    return asyncio.run(_calculate_inner())


# @app.task
# def calculate_registered_and_deposit_users(
#     dt_gt: date, dt_lt: date
# ) -> Dict[str, int]:
#     async def _calculate_inner():
#         async with get_session() as session:
#             users_count: int = await get_users_count_with_filters(
#                 session=session, dt_gt=dt_gt, dt_lt=dt_lt
#             )
#             return {"registered_and_deposit_users_count": users_count}
#
#     return asyncio.run(_calculate_inner())
@app.task
def calculate_registered_and_deposit_users(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    async def _calculate_inner():
        coroutines: List = []
        async with get_session() as session:
            for date_range in date_ranges:
                dt_gt, dt_lt = date_range
                coroutines.append(
                    get_users_count_with_filters(
                        session=session, dt_gt=dt_gt, dt_lt=dt_lt
                    )
                )
            users_count_values: List[int] = await asyncio.gather(*coroutines)
            return format_metrics_response(
                date_range=date_range,
                metric_name="registered_and_deposit_users_count",
                metric_values=users_count_values,
            )

    return asyncio.run(_calculate_inner())


# @app.task
# def calculate_registered_and_not_rollbacked_deposit_users(
#     dt_gt: date, dt_lt: date
# ) -> Dict[str, int]:
#     async def _calculate_inner():
#         async with get_session() as session:
#             users_count: int = await get_users_count_with_filters(
#                 session=session,
#                 dt_gt=dt_gt,
#                 dt_lt=dt_lt,
#                 exclude_rollbacked=True,
#             )
#             return {
#                 "registered_and_not_rollbacked_deposit_users_count": users_count
#             }
#
#     return asyncio.run(_calculate_inner())
@app.task
def calculate_registered_and_not_rollbacked_deposit_users(
    date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    async def _calculate_inner():
        coroutines: List = []
        async with get_session() as session:
            for date_range in date_ranges:
                dt_gt, dt_lt = date_range
                coroutines.append(
                    get_users_count_with_filters(
                        session=session,
                        dt_gt=dt_gt,
                        dt_lt=dt_lt,
                        exclude_rollbacked=True,
                    )
                )
            users_count_values: List[int] = await asyncio.gather(*coroutines)
            return format_metrics_response(
                date_range=date_range,
                metric_name="registered_and_not_rollbacked_deposit_users_count",
                metric_values=users_count_values,
            )

    return asyncio.run(_calculate_inner())
