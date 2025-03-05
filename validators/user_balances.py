from fastapi import status

from core.logger_configuration import app_logger
from exceptions.transactions import NegativeBalanceException
from models.users import UserBalance
from schemas.transactions import RequestTransactionModel


def validate_sufficient_balance(
    transaction: RequestTransactionModel, user_balance: UserBalance
) -> None:
    if user_balance.amount - transaction.amount < 0:
        app_logger.info("Not enough balance")
        raise NegativeBalanceException(
            message="Not enough balance", status_code=status.HTTP_403_FORBIDDEN
        )
