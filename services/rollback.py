from sqlalchemy.ext.asyncio import AsyncSession

from core.logger_configuration import app_logger
from models.transactions import Transaction
from models.users import UserBalance
from repositories.transactions import roll_back_transaction
from repositories.users_balances import restore_user_balance


async def make_roll_back(
    session: AsyncSession,
    transaction: Transaction,
    user_balance: UserBalance,
) -> Transaction:
    app_logger.info(
        f"Making roll back payment of transaction ID={transaction.id}"
        f" for user {user_balance.owner}"
    )
    roll_backed_transaction: Transaction = await roll_back_transaction(
        session=session,
        transaction=transaction,
    )
    await restore_user_balance(
        session=session,
        user_balance=user_balance,
        transaction=roll_backed_transaction,
    )
    app_logger.info(f"Roll back payment made for user {user_balance.owner}")
    return roll_backed_transaction
