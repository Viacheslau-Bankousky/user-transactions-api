"""
Module for transaction-related exceptions.

This module defines several custom exceptions, which inherit from the
`BaseAPIException` class. These exceptions are used to handle errors
that occur during transaction processing and related scenarios.
"""
from core.base_exception import BaseAPIException


class TransactionForBlockedUserException(BaseAPIException):
    """Raised when a transaction is attempted for a blocked user."""

    ...


class TransactionAlreadyRollbackedException(BaseAPIException):
    """
    Raised when a transaction has already been rolled back and a rollback attempt
     is attempted again.
    """

    ...


class NegativeBalanceException(BaseAPIException):
    """Raised when a transaction or operation results in a negative balance."""

    ...


class TransactionsNotFoundException(BaseAPIException):
    """Exception raised when the requested transactions are not found or missing."""

    ...
