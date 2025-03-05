from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession

from core.logger_configuration import app_logger
from models.transactions import Transaction
from models.users import UserBalance
from repositories.transactions import take_transaction
from repositories.users_balances import get_user_balance_for_currency
from schemas.transactions import RequestTransactionModel
from validators.transactions import (
    check_transaction_exists,
    check_transaction_rollbacked,
)
from validators.user_balances import validate_sufficient_balance
from validators.users import check_balance_owner_exists, check_user_is_active


async def ensure_valid_user_balance(
    session: AsyncSession, currency: str, user_id: int
) -> UserBalance:
    app_logger.info(f"Taking valid user balance for user {user_id}")
    user_balance: UserBalance | None = await get_user_balance_for_currency(
        session=session, user_id=user_id, currency=currency
    )
    check_balance_owner_exists(user_balance=user_balance)
    user_balance = cast(UserBalance, user_balance)
    check_user_is_active(user=user_balance.owner)
    app_logger.info(f"User balance taken for user {user_id}")

    return user_balance


async def ensure_valid_transaction(
    session: AsyncSession,
    user_id: int,
    transaction_id: int,
) -> Transaction:
    app_logger.info(
        f"Preparing transaction with id {transaction_id}"
        f" for user {user_id}"
    )
    user_transaction: Transaction | None = await take_transaction(
        session=session, user_id=user_id, id=transaction_id
    )
    check_transaction_exists(transaction=user_transaction)
    user_transaction = cast(Transaction, user_transaction)
    check_transaction_rollbacked(transaction=user_transaction)
    app_logger.info(f"Transaction prepared for user {user_id}")

    return user_transaction


async def ensure_payment_possibility(
    session: AsyncSession,
    user_id: int,
    transaction_data: RequestTransactionModel,
) -> UserBalance:
    app_logger.info(
        f"Preparing payment for user ID={user_id} with"
        f" currency={transaction_data.currency}"
    )
    user_balance: UserBalance = await ensure_valid_user_balance(
        session=session, currency=transaction_data.currency, user_id=user_id
    )
    validate_sufficient_balance(
        transaction=transaction_data,
        user_balance=user_balance,
    )
    app_logger.info(f"User balance prepared for user {user_id}")
    return user_balance


async def ensure_refund_possibility(
    session: AsyncSession,
    user_id: int,
    transaction_data: RequestTransactionModel,
) -> UserBalance:
    app_logger.info(
        f"Preparing refill funds for user ID={user_id} with currency="
        f" {transaction_data.currency}"
    )
    user_balance: UserBalance = await ensure_valid_user_balance(
        session=session, currency=transaction_data.currency, user_id=user_id
    )
    app_logger.info(f"User balance prepared for user ID={user_id}")

    return user_balance
