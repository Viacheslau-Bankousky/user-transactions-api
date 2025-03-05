from fastapi import status

from core.constants import NOTHING_WAS_FOUND_MESSAGE, USER_DOES_NOT_EXISTS
from core.logger_configuration import app_logger
from exceptions.transactions import TransactionForBlockedUserException
from exceptions.users import UserNotFoundException
from models.enums import UserStatusEnum
from models.users import User, UserBalance


def raise_if_none(condition: bool, log_message: str) -> None:
    if condition:
        app_logger.info(log_message)
        raise UserNotFoundException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=NOTHING_WAS_FOUND_MESSAGE,
        )


def check_balance_owner_exists(user_balance: UserBalance | None) -> None:
    raise_if_none(
        condition=not hasattr(user_balance, "owner"),
        log_message=USER_DOES_NOT_EXISTS,
    )


def check_user_exists(user: User | None) -> None:
    raise_if_none(
        condition=not user,
        log_message=USER_DOES_NOT_EXISTS,
    )


def check_user_is_active(user: User | None) -> None:
    if user and user.status != UserStatusEnum.ACTIVE:
        app_logger.info("An attempt to deposit to blocked user was made.")
        raise TransactionForBlockedUserException(
            status_code=status.HTTP_403_FORBIDDEN,
            message="User is blocked",
        )


def validate_user_status(user_status: str) -> None:
    if user_status not in UserStatusEnum:
        app_logger.info("Invalid status value was passed:")
        raise UserNotFoundException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=NOTHING_WAS_FOUND_MESSAGE,
        )
