from datetime import date
from typing import Dict

from core.database import get_session
from repositories.users import (
    get_registered_users_count,
    get_users_count_with_filters,
)
from statistic.worker import app


@app.task
async def calculate_registered_users(
    dt_gt: date, dt_lt: date
) -> Dict[str, int]:
    async with get_session() as session:
        users_count: int = await get_registered_users_count(
            session=session, dt_gt=dt_gt, dt_lt=dt_lt
        )
        return {"registered_users_count": users_count}


@app.task
async def calculate_registered_and_deposit_users(
    dt_gt: date, dt_lt: date
) -> Dict[str, int]:
    async with get_session() as session:
        users_count: int = await get_users_count_with_filters(
            session=session, dt_gt=dt_gt, dt_lt=dt_lt
        )
        return {"registered_and_deposit_users_count": users_count}


@app.task
async def calculate_registered_and_not_rollbacked_deposit_users(
    dt_gt: date, dt_lt: date
) -> Dict[str, int]:
    async with get_session() as session:
        users_count: int = await get_users_count_with_filters(
            session=session, dt_gt=dt_gt, dt_lt=dt_lt, exclude_rollbacked=True
        )
        return {
            "registered_and_not_rollbacked_deposit_users_count": users_count
        }
