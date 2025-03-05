from sqlalchemy.ext.asyncio import AsyncSession

from core.logger_configuration import app_logger
from models.transactions import Transaction
from models.users import UserBalance
from repositories.transactions import create_transaction
from repositories.users_balances import reduce_user_balance
from schemas.transactions import RequestTransactionModel
from services.preconditions import (
    ensure_payment_possibility,
)


async def make_payment(
    session: AsyncSession,
    transaction_data: RequestTransactionModel,
    user_id: int,
    user_balance: UserBalance,
) -> Transaction:
    app_logger.info(
        f"Making payment for user ID={user_id} "
        f"with currency={transaction_data.currency}"
    )
    transaction: Transaction = await create_transaction(
        session=session, transaction_data=transaction_data, user_id=user_id
    )
    await reduce_user_balance(
        session=session, user_balance=user_balance, transaction=transaction
    )
    app_logger.info(f"Payment made for user {user_id}")
    return transaction


async def process_payment(
    session: AsyncSession,
    user_id: int,
    transaction_data: RequestTransactionModel,
):
    app_logger.info(f"Processing payment for user ID={user_id}")
    user_balance: UserBalance = await ensure_payment_possibility(
        session=session, user_id=user_id, transaction_data=transaction_data
    )
    new_transaction: Transaction = await make_payment(
        session=session,
        transaction_data=transaction_data,
        user_id=user_id,
        user_balance=user_balance,
    )
    app_logger.info(f"Payment processed for user ID={user_id}")
    return new_transaction
