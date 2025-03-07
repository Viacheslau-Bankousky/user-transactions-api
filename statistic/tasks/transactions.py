from datetime import date
from decimal import Decimal
from typing import Dict

from core.database import get_session
from models.enums import TransactionPurposeEnum
from repositories.transactions import (
    get_not_rollbacked_transactions_amount,
    get_not_rollbacked_transactions_count,
    get_transactions_count,
)
from statistic.worker import app


@app.task
async def calculate_transactions(dt_gt: date, dt_lt: date) -> Dict[str, int]:
    async with get_session() as session:
        transactions_count: int = await get_transactions_count(
            session=session, dt_gt=dt_gt, dt_lt=dt_lt
        )
        return {"transactions_count": transactions_count}


@app.task
async def calculate_not_rollbacked_transactions(
    dt_gt: date, dt_lt: date
) -> Dict[str, int]:
    async with get_session() as session:
        transactions_count: int = await get_not_rollbacked_transactions_count(
            session=session, dt_gt=dt_gt, dt_lt=dt_lt
        )
        return {"not_rollbacked_transactions_count": transactions_count}


@app.task
async def calculate_not_rollbacked_deposit_amount(
    dt_gt: date, dt_lt: date
) -> Dict[str, str]:
    async with get_session() as session:
        deposit_amount: Decimal = await get_not_rollbacked_transactions_amount(
            session=session,
            dt_gt=dt_gt,
            dt_lt=dt_lt,
            transaction_purpose=TransactionPurposeEnum.REFUND,
        )
        return {"not_rollbacked_deposit_amount": str(deposit_amount)}


@app.task
async def calculate_not_rollbacked_withdraw_amount(
    dt_gt: date, dt_lt: date
) -> Dict[str, str]:
    async with get_session() as session:
        deposit_amount: Decimal = await get_not_rollbacked_transactions_amount(
            session=session,
            dt_gt=dt_gt,
            dt_lt=dt_lt,
            transaction_purpose=TransactionPurposeEnum.WITHDRAWAL,
        )
        return {"not_rollbacked_withdraw_amount": str(deposit_amount)}
