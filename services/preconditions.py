"""
Module for validating and ensuring payment and transaction conditions.

This module provides a set of asynchronous functions to validate and
ensure various preconditions for payments, refunds, and transactions.
These functions utilize validators to perform checks like verifying
user balances, transaction existence, sufficient balance availability,
and user account status.

Key Features:
- **User Balance Validation**: Ensures a user has a valid and active
 balance account in the specified currency.
- **Transaction Validation**: Verifies the existence and status of a
 transaction, including checks for previously rolled-back transactions.
- **Payment and Refund Validation**: Ensures the user has sufficient
 funds or can proceed with a refund process.

Dependencies:
- SQLAlchemy's `AsyncSession` is used for asynchronous database
 operations.
- Validators are used to encapsulate business rules, such as
 checking whether a user balance exists or if a user account is active.
- Logging is handled through the central logger (`app_logger`)
 for detailed traceability.

Functions:
- **ensure_valid_user_balance**: Checks if the user has a valid balance
 account for a given currency and verifies the user is active.
- **ensure_valid_transaction**: Ensures a transaction exists for a user
 and is not rolled back.
- **ensure_payment_possibility**: Validates that a payment can be made
 by checking the user balance and ensuring sufficient funds are available.
- **ensure_refund_possibility**: Validates if a refund process can proceed
 for a user.
"""

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
    """
    Ensure a user has a valid balance account in the specified currency.

    Also, this coroutine verifies the associated user is active.

    Args:
        session (AsyncSession): The database session for querying user
            balance data.
        currency (str): The currency in which the balance is being
            validated.
        user_id (int): The ID of the user associated with the balance.

    Returns:
        UserBalance: The valid and active user balance for the specified
            currency.

    """
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
    """
    Ensure a transaction exists for the user.

    Also, this coroutine verifies the validated transaction has not been
    rolled back.

    Args:
        session (AsyncSession): The database session for querying
            transaction data.
        user_id (int): The ID of the user associated with the transaction.
        transaction_id (int): The ID of the transaction to validate.

    Returns:
        Transaction: The valid transaction for the user.
    """
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
    """
    Ensure a payment is possible for the user by validating the balance.

    Also, this coroutine performs additional checks, including
    checking sufficient funds for the transaction.

    Args:
        session (AsyncSession): The database session for querying user
            balance data.
        user_id (int): The ID of the user initiating the payment.
        transaction_data (RequestTransactionModel): The transaction details
            including amount and currency.

    Returns:
        UserBalance: The validated user balance with sufficient funds.
    """
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
    """
    Ensure a refund process is possible for the user by validating the balance.

    Args:
        session (AsyncSession): The database session for querying user
            balance data.
        user_id (int): The ID of the user for whom the refund
            is being processed.
        transaction_data (RequestTransactionModel): The transaction
            details including amount and currency.

    Returns:
        UserBalance: The validated user balance.
    """
    app_logger.info(
        f"Preparing refill funds for user ID={user_id} with currency="
        f" {transaction_data.currency}"
    )
    user_balance: UserBalance = await ensure_valid_user_balance(
        session=session, currency=transaction_data.currency, user_id=user_id
    )
    app_logger.info(f"User balance prepared for user ID={user_id}")

    return user_balance
