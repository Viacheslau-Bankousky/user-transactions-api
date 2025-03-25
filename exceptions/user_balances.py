"""
Module for exceptions related to user balance.

This module defines a custom exception used to handle errors related to
the absence of a user's balance in the system.
"""

from core.base_exception import BaseAPIException


class UserBalanceDoesNotExistException(BaseAPIException):
    """Raised when a user's balance record is not found in the system. """

    ...
