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
    if condition:
        app_logger.info(log_message)
        raise TransactionsNotFoundException(
            message=NOTHING_WAS_FOUND_MESSAGE,
            status_code=status.HTTP_404_NOT_FOUND,
        )


def check_transactions_exist(transactions: Sequence[Transaction]) -> None:
    raise_if_none(
        condition=not transactions,
        log_message=NOTHING_WAS_FOUND_MESSAGE,
    )


def check_transaction_exists(transaction: Transaction | None) -> None:
    raise_if_none(
        condition=not transaction,
        log_message=NOTHING_WAS_FOUND_MESSAGE,
    )


def check_transaction_status(transaction_status: str) -> None:
    if transaction_status not in TransactionStatusEnum:
        app_logger.info("Invalid status value was passed:")
        raise BadRequestDataException(
            message="Invalid status",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


def check_transaction_rollbacked(transaction: Transaction) -> None:
    if transaction.status == TransactionStatusEnum.ROLL_BACKED:
        app_logger.info(
            "An attempt to rollback rollbacked transaction was made."
        )
        raise TransactionAlreadyRollbackedException(
            message="Transaction already rollbacked",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
