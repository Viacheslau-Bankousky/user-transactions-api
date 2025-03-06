from datetime import date
from decimal import Decimal
from typing import List, Sequence, Tuple

from sqlalchemy import Result, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import BinaryExpression

from models.enums import TransactionPurposeEnum, TransactionStatusEnum
from models.transactions import Transaction
from repositories.query_builder import (
    get_date_range_filter,
    prepare_filtered_query,
)
from schemas.transactions import RequestTransactionModel


async def take_transactions(
    session: AsyncSession, **filter_params
) -> Sequence[Transaction]:
    query: Select[Tuple[Transaction]] = prepare_filtered_query(
        model=Transaction, **filter_params
    )
    transactions: Result[Tuple[Transaction]] = await session.execute(query)
    return transactions.scalars().all()


async def create_transaction(
    session: AsyncSession,
    transaction_data: RequestTransactionModel,
    user_id: int,
) -> Transaction:
    transaction = Transaction(user_id=user_id, **transaction_data.model_dump())
    session.add(transaction)
    await session.flush()

    return transaction


async def take_transaction(
    session: AsyncSession, **filter_params
) -> Transaction | None:
    query: Select[Tuple[Transaction]] = prepare_filtered_query(
        model=Transaction, **filter_params
    )
    transaction: Result[Tuple[Transaction]] = await session.execute(query)
    return transaction.scalars().first()


async def roll_back_transaction(
    session: AsyncSession,
    transaction: Transaction,
) -> Transaction:
    transaction.status = TransactionStatusEnum.ROLL_BACKED
    session.add(transaction)
    await session.flush()

    return transaction


async def get_transactions_count(
    session: AsyncSession, dt_gt: date, dt_lt: date
) -> int:
    query: Select = select(func.count(Transaction.id)).where(
        get_date_range_filter(
            date_from=dt_gt, date_to=dt_lt, model=Transaction
        )
    )
    transactions_result: Result = await session.execute(query)
    transactions_count: int = transactions_result.scalar()
    return transactions_count


async def get_not_rollbacked_transactions_count(
    session: AsyncSession, dt_gt: date, dt_lt: date
) -> int:
    query: Select = select(func.count(Transaction.id)).where(
        get_date_range_filter(
            date_from=dt_gt, date_to=dt_lt, model=Transaction
        ),
        Transaction.status != TransactionStatusEnum.ROLL_BACKED,
    )
    transactions_result: Result = await session.execute(query)
    transactions_count: int = transactions_result.scalar()
    return transactions_count


async def get_not_rollbacked_transactions_amount(
    session: AsyncSession,
    dt_gt: date,
    dt_lt: date,
    transaction_purpose: TransactionPurposeEnum,
) -> Decimal:
    conditions: List[BinaryExpression] = [
        get_date_range_filter(
            date_from=dt_gt, date_to=dt_lt, model=Transaction
        ),
        Transaction.status != TransactionStatusEnum.ROLL_BACKED,
    ]
    if transaction_purpose == TransactionPurposeEnum.REFUND:
        conditions.append(Transaction.purpose == transaction_purpose)
    elif transaction_purpose == TransactionPurposeEnum.WITHDRAWAL:
        conditions.append(Transaction.purpose == transaction_purpose)

    query: Select = select(func.sum(Transaction.amount)).where(*conditions)
    transactions_result: Result = await session.execute(query)
    transactions_amount: Decimal | None = transactions_result.scalar()
    return transactions_amount if transactions_amount else Decimal(0)
