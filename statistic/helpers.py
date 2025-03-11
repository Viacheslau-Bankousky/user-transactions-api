import asyncio
from datetime import date, timedelta
from typing import Any, Awaitable, Callable, Dict, List, Tuple

from core.database import get_session


def generate_date_ranges(weeks_count: int) -> List[Tuple[date, date]]:
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


# def format_metrics_response(
#     date_ranges: List[Tuple[date, date]],
#     metric_name: str,
#     metric_values: List[int],
# ) -> List[Dict[str, str]]:
#     response_data: List[dict] = []
#     for index, date_range in enumerate(date_ranges):
#         start_date, end_date = date_range
#         response_data.append(
#             {
#                 "start_date": start_date,
#                 "end_date": end_date,
#                 metric_name: str(metric_values[index]),
#             }
#         )
#     return response_data


def run_in_loop(coro: Awaitable[Any]) -> Any:
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)


# async def process_date_ranges_with_session(
#     date_ranges: List[Tuple[date, date]],
#     metric_function: Callable,
#     **kwargs,
# ) -> List[Any]:
#     async def process_single_range(dt_gt: date, dt_lt: date) -> Any:
#         async with get_session() as session:
#             return await metric_function(session, dt_gt, dt_lt, **kwargs)
#
#     coroutines = [
#         process_single_range(dt_gt, dt_lt) for dt_gt, dt_lt in date_ranges
#     ]
#     results: List[Any] = await asyncio.gather(*coroutines)
#
#     return results

async def process_date_range_with_session(
    dt_gt: date, dt_lt: date,
    metric_function: Callable,
    **kwargs,
) -> List[Any]:
    async with get_session() as session:
        return await metric_function(session, dt_gt, dt_lt, **kwargs)
