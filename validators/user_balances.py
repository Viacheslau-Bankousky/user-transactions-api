"""
Module for validating user balance against transaction amounts.

This module provides a utility function to ensure that a user's
 balance is sufficient to cover the specified transaction amount.
If the balance is insufficient, the function raises a custom
exception with an appropriate error message and logs the issue.

Key Features:
- **Balance Validation**: Checks if the user has enough balance for
 a transaction.
- **Custom Exceptions**: Raises a `NegativeBalanceException` with a
 `403 Forbidden` status code if the balance is insufficient.
- **Logging**: Logs a message when the balance is insufficient to help
  with debugging and traceability.

Dependencies:
- FastAPI's `status` for HTTP response codes.
- Custom `NegativeBalanceException` for insufficient balance errors.
- Logging is handled through the application’s central logger
 (`app_logger`).

Function:
- **validate_sufficient_balance**: Validates if the user's balance
 is sufficient for the transaction.
"""

from fastapi import status

from core.logger_configuration import app_logger
from exceptions.transactions import NegativeBalanceException
from models.users import UserBalance
from schemas.transactions import RequestTransactionModel


def validate_sufficient_balance(
    transaction: RequestTransactionModel, user_balance: UserBalance
) -> None:
    """
    Validate that a user's balance is sufficient for a transaction.

    This function checks if the user's current balance is enough to
    cover the transaction amount. If the balance is insufficient,
    it raises a `NegativeBalanceException`.

    Args:
        transaction (RequestTransactionModel): The transaction
            containing the amount to be deducted.
        user_balance (UserBalance): The user's balance record.

    Raises:
        NegativeBalanceException: If the user's balance is insufficient.
    """
    if user_balance.amount - transaction.amount < 0:
        app_logger.info("Not enough balance")
        raise NegativeBalanceException(
            message="Not enough balance", status_code=status.HTTP_403_FORBIDDEN
        )
