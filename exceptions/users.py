"""This module defines custom exceptions for user-related operations."""
from core.base_exception import BaseAPIException


class UserAlreadyExistsException(BaseAPIException):
    """Exception raised when a user already exists."""

    ...


class UserNotFoundException(BaseAPIException):
    """Exception raised when the requested user cannot be found."""

    ...
