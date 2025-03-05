from typing import Tuple

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from models.enums import TransactionPurposeEnum
from models.transactions import Transaction
from models.users import UserBalance


async def get_user_balance_for_currency(
    session: AsyncSession, user_id: int, currency: str
) -> UserBalance:
    query: Select[Tuple[UserBalance]] = select(UserBalance).where(
        (UserBalance.user_id == user_id) & (UserBalance.currency == currency)
    )
    user_balance: Result[Tuple[UserBalance]] = await session.execute(query)
    return user_balance.scalars().first()  # type: ignore


async def reduce_user_balance(
    session: AsyncSession, user_balance: UserBalance, transaction: Transaction
) -> None:
    user_balance.amount -= transaction.amount
    session.add(user_balance)
    await session.flush()


async def restore_user_balance(
    session: AsyncSession, user_balance: UserBalance, transaction: Transaction
) -> None:
    if transaction.purpose == TransactionPurposeEnum.REFUND:
        user_balance.amount -= transaction.amount
    elif transaction.purpose == TransactionPurposeEnum.WITHDRAWAL:
        user_balance.amount += transaction.amount

    session.add(user_balance)
    await session.flush()


async def increase_user_balance(
    session: AsyncSession, user_balance: UserBalance, transaction: Transaction
) -> None:
    user_balance.amount += transaction.amount
    session.add(user_balance)
    await session.flush()
