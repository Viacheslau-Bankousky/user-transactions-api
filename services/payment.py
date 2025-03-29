"""
Module for handling payment processing and transactions.

This module provides asynchronous functions that manage payment workflows,
including creating transactions, updating user balances, and validating
payment conditions.
It utilizes a layered approach by integrating repositories for database
operations and services for business logic.

Key Features:
- **Payment Workflow**: Functions to process and execute payments for users.
- **Validation Support**: Ensures payments are possible before proceeding,
  including balance checks and currency validations.
- **Database Integration**: Handles persistence of transaction data and
  updates to user balances with the use of repositories.
- **Logging**: Provides detailed logging for tracking payment processes.

Dependencies:
- The module uses `AsyncSession` for database operations with SQLAlchemy.
- Custom repository and service modules are utilized for managing specific
  functionalities such as creating transactions and reducing user balances.
- Logging is handled using the application's centralized logger, `app_logger`.

Functions:
- **make_payment**: Executes the payment by creating a transaction record and
  reducing the user's account balance accordingly.
- **process_payment**: Manages the entire payment workflow, including
 preconditions, transaction creation, and balance updates.
"""

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
    """
    Execute the payment process for a user.

    This function creates a new transaction record and updates the user's
    balance by deducting the transaction amount.
    It ensures all operations are logged.

    Args:
        session (AsyncSession): The database session for managing transactions.
        transaction_data (RequestTransactionModel): Details of the transaction
            to be created.
        user_id (int): The ID of the user initiating the transaction.
        user_balance (UserBalance): The current balance of the user.

    Returns:
        Transaction: The newly created transaction record.
    """
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
) -> Transaction:
    """
    Process the payment workflow for a user.

    This function manages the complete payment flow, including:
        - Validating the user's ability to make the payment.
        - Creating a new transaction record.
        - Updating the user's balance.

    Args:
        session (AsyncSession): The database session for managing
            transactions.
        user_id (int): The ID of the user initiating the payment.
        transaction_data (RequestTransactionModel): Details of the
            requested transaction.

    Returns:
        Transaction: The transaction record created after successful
            processing.
    """
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
