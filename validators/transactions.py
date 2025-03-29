"""
Module for validating transactions.

This module contains utility functions for validating transaction objects
and statuses.
It raises custom exceptions if the validation fails.
Logging is implemented to assist with debugging and tracking validation
failures.

Key Features:
- **Existence Checks**: Validates the existence of transactions and raises
  exceptions if they are not found.
- **Status Validation**: Ensures that the provided transaction status is
 valid and checks whether transactions have already been rolled back.
- **Logging**: Logs validation steps and failures for better traceability
  and debugging.

Dependencies:
- FastAPI's `status` for HTTP response codes.
- Custom exceptions like `TransactionsNotFoundException`,
  `TransactionAlreadyRollbackedException`, and `BadRequestDataException`.
- Logging is managed through the application’s central logger (`app_logger`).

Functions:
- **raise_if_none**: A helper to raise an exception if a condition evaluates
 to `True`.
- **check_transactions_exist**: Checks if a sequence of transactions exists.
- **check_transaction_exists**: Validates the existence of a specific
 transaction.
- **check_transaction_status**: Checks if a transaction status is valid.
- **check_transaction_rollbacked**: Ensures that a transaction has not
 already been rolled back.
"""

from typing import Sequence

from fastapi import status

from core.constants import NOTHING_WAS_FOUND_MESSAGE
from core.logger_configuration import app_logger
from exceptions.transactions import (
    TransactionAlreadyRollbackedException,
    TransactionsNotFoundException,
)
from exceptions.validation import BadRequestDataException
from models.enums import TransactionStatusEnum
from models.transactions import Transaction


def raise_if_none(condition: bool, log_message: str) -> None:
    """
    Raise an exception if the specified condition is `True`.

    Args:
        condition (bool): The condition to evaluate.
        log_message (str): The message to log before raising the exception.

    Raises:
        TransactionsNotFoundException: If the condition evaluates to `True`.
    """
    if condition:
        app_logger.info(log_message)
        raise TransactionsNotFoundException(
            message=log_message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


def check_transactions_exist(transactions: Sequence[Transaction]) -> None:
    """
    Check if a sequence of transactions exists.

    This function raises an exception if the `transactions` sequence
    is empty.

    Args:
        transactions (Sequence[Transaction]): A sequence
            of Transaction objects.

    Raise:
        TransactionsNotFoundException: If no transactions are found.
    """
    raise_if_none(
        condition=not transactions,
        log_message=NOTHING_WAS_FOUND_MESSAGE,
    )


def check_transaction_exists(transaction: Transaction | None) -> None:
    """
    Validate that a specific transaction exists.

    This function raises an exception if the `transaction` is `None`.

    Args:
        transaction (Transaction | None): The transaction to validate.

    Raise:
        TransactionsNotFoundException: If the transaction is `None`.
    """
    raise_if_none(
        condition=not transaction,
        log_message=NOTHING_WAS_FOUND_MESSAGE,
    )


def check_transaction_status(transaction_status: str) -> None:
    """
    Validate that the given transaction status is valid.

    This function raises an exception if the provided `transaction_status`
    does not belong to the `TransactionStatusEnum`.

    Args:
        transaction_status (str): The transaction status to validate.

    Raises:
        BadRequestDataException: If the status is invalid.
    """
    if transaction_status not in TransactionStatusEnum:
        app_logger.info("Invalid status value was passed:")
        raise BadRequestDataException(
            message="Invalid status",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


def check_transaction_rollbacked(transaction: Transaction) -> None:
    """
     Validate that the transaction has not been rolled back.

    This function raises an exception if the `transaction` is
    already in the "rolled-back" status.

    Args:
        transaction (Transaction): The transaction to validate.

    Raises:
        TransactionAlreadyRollbackedException: If the transaction has
            already been rolled back.
    """
    if transaction.status == TransactionStatusEnum.ROLL_BACKED:
        app_logger.info(
            "An attempt to rollback rollbacked transaction was made."
        )
        raise TransactionAlreadyRollbackedException(
            message="Transaction already rollbacked",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
