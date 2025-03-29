"""
Module for validating user-related data.

This module provides utility functions for validating users,
their statuses, and their associations with balances to ensure
data integrity and proper business logic handling.
If validations fail, appropriate custom exceptions are raised.
All major actions are logged for better traceability.

Key Features:
- **Existence Checks**: Validates the existence of users, balances,
 and balance owners.
- **Status Validation**: Ensures that user status values are valid
 and that users are active.
- **Custom Exceptions**: Raises exceptions for not found users,
 invalid statuses, or blocked users.
- **Logging**: Logs validation failures and important actions
 for debugging purposes.

Dependencies:
- FastAPI's `status` for HTTP response codes.
- Custom exceptions like `UserNotFoundException` and
 `TransactionForBlockedUserException`.
- Logging handled through the centralized application logger
 (`app_logger`).

Functions:
- **raise_if_none**: Helper function to raise an exception if
 a condition is `True`.
- **check_balance_owner_exists**: Validates that a balance has an owner.
- **check_user_exists**: Validates the existence of a user instance.
- **check_user_is_active**: Ensures the user is active (not blocked).
- **validate_user_status**: Validates that the user status is valid.
"""

from fastapi import status

from core.constants import NOTHING_WAS_FOUND_MESSAGE, USER_DOES_NOT_EXISTS
from core.logger_configuration import app_logger
from exceptions.transactions import TransactionForBlockedUserException
from exceptions.users import UserNotFoundException
from models.enums import UserStatusEnum
from models.users import User, UserBalance


def raise_if_none(condition: bool, log_message: str) -> None:
    """
    Raise an exception if the specified condition is `True`.

    Args:
        condition (bool): The condition to evaluate.
        log_message (str): The message to log before raising
            the exception.

    Raises:
        UserNotFoundException: If the condition evaluates to `True`.
    """
    if condition:
        app_logger.info(log_message)
        raise UserNotFoundException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=NOTHING_WAS_FOUND_MESSAGE,
        )


def check_balance_owner_exists(user_balance: UserBalance | None) -> None:
    """
    Validate that the balance object has an associated owner.

    This function raises an exception if the `user_balance` does not
    have an `owner` attribute.

    Args:
        user_balance (UserBalance | None): The user balance to check.

    Raise:
        UserNotFoundException: If the balance owner does not exist.
    """
    raise_if_none(
        condition=not hasattr(user_balance, "owner"),
        log_message=USER_DOES_NOT_EXISTS,
    )


def check_user_exists(user: User | None) -> None:
    """
    Validate the existence of a user instance.

    This function raises an exception if the `user` is `None`.

    Args:
        user (User | None): The user to validate.

    Raise:
        UserNotFoundException: If the user does not exist.
    """
    raise_if_none(
        condition=not user,
        log_message=USER_DOES_NOT_EXISTS,
    )


def check_user_is_active(user: User | None) -> None:
    """
    Validate that the user is active (not blocked).

    This function raises an exception if the user exists but their status
    is not `ACTIVE`.

    Args:
        user (User | None): The user to check.

    Raises:
        TransactionForBlockedUserException: If the user is blocked.
    """
    if user and user.status != UserStatusEnum.ACTIVE:
        app_logger.info("An attempt to deposit to blocked user was made.")
        raise TransactionForBlockedUserException(
            status_code=status.HTTP_403_FORBIDDEN,
            message="User is blocked",
        )


def validate_user_status(user_status: str) -> None:
    """
    Validate that the specified user status is valid.

    This function raises an exception if the `user_status`
    does not belong to `UserStatusEnum`.

    Args:
        user_status (str): The user status to validate.

    Raises:
        UserNotFoundException: If the user status is invalid.
    """
    if user_status not in UserStatusEnum:
        app_logger.info("Invalid status value was passed:")
        raise UserNotFoundException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=NOTHING_WAS_FOUND_MESSAGE,
        )
