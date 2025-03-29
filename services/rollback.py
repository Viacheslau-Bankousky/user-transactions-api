"""
Module for handling transaction rollbacks.

This module provides an asynchronous function to manage the rollback
process for transactions.
The rollback process involves reversing the effects of a transaction,
such as restoring user balances, and updating the transaction status
in the database.

Key Features:
- **Transaction Rollback**: Supports undoing transactions by marking
 them as rolled back and restoring the associated user balance.
- **User Balance Restoration**: Ensures that the funds involved in
 the transaction are accurately returned to the user's balance.
- **Logging**: Logs each step of the rollback process for tracking
 and debugging.

Dependencies:
- SQLAlchemy's `AsyncSession` is used for database operations.
- Repository functions handle specific database updates for
 transactions and user balances.
- Logging is managed by the application’s centralized logger
 (`app_logger`).

Function:
- **make_roll_back**: Executes the rollback of a transaction
 and restores the user's balance.
"""

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
    """
    Execute the rollback of a specified transaction.

    This function reverses the specified transaction by marking it
    as rolled back in the database and restoring the funds to the
    user's balance. All steps are logged for traceability.

    Args:
        session (AsyncSession): The database session for managing
            transactions.
        transaction (Transaction): The transaction to be rolled back.
        user_balance (UserBalance): The balance of the user involved
            in the transaction.

    Returns:
        Transaction: The updated transaction marked as rolled back.
    """
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
