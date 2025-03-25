"""This module defines custom exceptions for user-related operations."""
from core.base_exception import BaseAPIException


class UserAlreadyExistsException(BaseAPIException):
    """Raised when a user already exists."""

    ...


class UserNotFoundException(BaseAPIException):
    """Raised when the requested user cannot be found."""

    ...
