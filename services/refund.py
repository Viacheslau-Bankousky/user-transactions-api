"""
Module for handling refund processes and transactions.

This module provides asynchronous functions to manage and execute
the refund workflow.
Refunds are processed by creating new transaction records and
updating user balances appropriately.
The workflow ensures the necessary preconditions are validated,
and the operations are logged for tracking.

Key Features:
- **Refund Workflow**: Supports the validation and execution
 of refund requests for users.
- **Transaction Management**: Creates records for refund
 transactions in the system.
- **User Balance Updates**: Handles the increase of user
 balances after successful refunds.
- **Logging**: Logs important steps during the refund
 process for better traceability.

Dependencies:
- SQLAlchemy's `AsyncSession` is used for database operations.
- Precondition checks ensure user balance validity and readiness
 for a refund.
- Logging is handled with the application’s central logger
 (`app_logger`).

Functions:
- **make_refund**: Executes the refund by creating a transaction
 and increasing the user's balance.
- **process_refund**: Manages the entire refund workflow, including
 validation, transaction creation, and balance updates.
"""

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
    """
    Execute the refund process for a user.

    This function creates a refund transaction record and updates
    the user’s balance by increasing the specified amount.
    All steps are logged for transparency and troubleshooting.

    Args:
        session (AsyncSession): The database session for managing
            transactions.
        transaction_data (RequestTransactionModel): Details of the
            refund transaction such as amount and currency.
        user_id (int): The ID of the user initiating the refund.
        user_balance (UserBalance): The user's current balance
            to be updated.

    Returns:
        Transaction: The newly created refund transaction record.
    """
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
) -> Transaction:
    """
    Process the refund workflow for a user.

    This function validates that the refund is possible by ensuring the user
    has a valid balance in the relevant currency.
    Once validated, it creates a refund transaction and updates the user’s
    balance.

    Args:
        session (AsyncSession): The database session for managing
            transactions.
        user_id (int): The ID of the user requesting the refund.
        transaction_data (RequestTransactionModel): The transaction
            details, including the refund amount and currency.

    Returns:
        Transaction: The transaction record for the completed refund.
    """
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
