import asyncio
from datetime import date
from typing import Any, Callable, List, Tuple

from core.database import get_session


async def process_date_ranges_with_session(
    date_ranges: List[Tuple[date, date]],
    metric_function: Callable,
    **kwargs,
) -> List[Any]:
    async def process_single_range(dt_gt: date, dt_lt: date) -> Any:
        async with get_session() as session:
            return await metric_function(session, dt_gt, dt_lt, **kwargs)

    coroutines = [
        process_single_range(dt_gt, dt_lt) for dt_gt, dt_lt in date_ranges
    ]
    results: List[Any] = await asyncio.gather(*coroutines)

    return results
