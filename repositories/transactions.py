from typing import Sequence, Tuple

from sqlalchemy import Result, Select
from sqlalchemy.ext.asyncio import AsyncSession

from models.enums import TransactionStatusEnum
from models.transactions import Transaction
from repositories.query_builder import prepare_filtered_query
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
    transaction = Transaction(
        user_id=user_id, **transaction_data.model_dump()
    )
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


# async def get_transactions_count(
#     session: AsyncSession, dt_gt: date, dt_lt: date
# ):
#     q = select(Transaction).where(
#         (func.date(Transaction.created) >= dt_gt)
#         & (func.date(Transaction.created) <= dt_lt)
#     )
#     transactions = await session.execute(q)
#     transactions = transactions.fetchall()
#     return len(transactions)
#
#
# async def get_not_rollbacked_transactions_count(
#     session: AsyncSession, dt_gt: date, dt_lt: date
# ):
#     q = select(Transaction).where(
#         (func.date(Transaction.created) >= dt_gt)
#         & (func.date(Transaction.created) <= dt_lt)
#         & (Transaction.status != "ROLLBACKED")
#     )
#     transactions = await session.execute(q)
#     transactions = transactions.fetchall()
#     return len(transactions)

# async def get_not_rollbacked_withdraw_amount(
#     session: AsyncSession, dt_gt: date, dt_lt: date
# ):
#     q = select(Transaction).where(
#         (func.date(Transaction.created) >= dt_gt)
#         & (func.date(Transaction.created) <= dt_lt)
#         & (Transaction.amount < 0)
#         & (Transaction.status != "ROLLBACKED")
#     )
#     not_rollbacked_withdraws = await session.execute(q)
#     not_rollbacked_withdraws = not_rollbacked_withdraws.scalars()
#     return sum(
#         [
#             x.amount * EXCHANGE_RATES_TO_USD[x.currency]
#             for x in not_rollbacked_withdraws
#         ]
#     )
#
# async def get_registered_and_not_rollbacked_deposit_users_count(
#     session: AsyncSession, dt_gt: date, dt_lt: date
# ):
#     result = 0
#     q = select(User).where(
#         (func.date(User.created >= dt_gt)) & (func.date(User.created) <= dt_lt)
#     )
#     registered_users = await session.execute(q)
#     registered_users = registered_users.scalars()
#     for user in registered_users:
#         q = select(Transaction).where(
#             (func.date(Transaction.created) >= dt_gt)
#             & (func.date(Transaction.created) <= dt_lt)
#             & (Transaction.user_id == user.id)
#             & (Transaction.amount > 0)
#             & (Transaction.status != "ROLLBACKED")
#         )
#         not_rollbacked_deposits = await session.execute(q)
#         not_rollbacked_deposits = not_rollbacked_deposits.fetchall()
#         if len(not_rollbacked_deposits) > 0:
#             result += 1
#     return result
#
#
# async def get_not_rollbacked_deposit_amount(
#     session: AsyncSession, dt_gt: date, dt_lt: date
# ):
#     q = select(Transaction).where(
#         (func.date(Transaction.created) >= dt_gt)
#         & (func.date(Transaction.created) <= dt_lt)
#         & (Transaction.amount > 0)
#         & (Transaction.status != "ROLLBACKED")
#     )
#     not_rollbacked_deposits = await session.execute(q)
#     not_rollbacked_deposits = not_rollbacked_deposits.scalars()
#     return sum(
#         [
#             x.amount * EXCHANGE_RATES_TO_USD[x.currency]
#             for x in not_rollbacked_deposits
#         ]
#     )
