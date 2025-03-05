from sqlalchemy.ext.asyncio import AsyncSession

from core.logger_configuration import app_logger
from models.transactions import Transaction
from models.users import UserBalance
from repositories.transactions import create_transaction
from repositories.users_balances import increase_user_balance
from schemas.transactions import RequestTransactionModel
from services.preconditions import ensure_refund_possibility


async def make_refund(
    session: AsyncSession,
    transaction_data: RequestTransactionModel,
    user_id: int,
    user_balance: UserBalance,
) -> Transaction:
    app_logger.info(
        f"Making refill funds for user Id={user_id}"
        f" with currency={transaction_data.currency}"
    )
    new_transaction: Transaction = await create_transaction(
        session=session, transaction_data=transaction_data, user_id=user_id
    )
    await increase_user_balance(
        session=session, user_balance=user_balance, transaction=new_transaction
    )
    app_logger.info(f"Refill made successfully for user ID={user_id}")

    return new_transaction


async def process_refund(
    session: AsyncSession,
    user_id: int,
    transaction_data: RequestTransactionModel,
):
    app_logger.info(f"Processing refill funds for user ID={user_id}")
    user_balance: UserBalance = await ensure_refund_possibility(
        session=session, user_id=user_id, transaction_data=transaction_data
    )
    new_transaction: Transaction = await make_refund(
        session=session,
        user_id=user_id,
        transaction_data=transaction_data,
        user_balance=user_balance,
    )
    app_logger.info(f"Refill processed for user ID={user_id}")

    return new_transaction
