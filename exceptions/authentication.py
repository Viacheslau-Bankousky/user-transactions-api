"""
This module defines custom exceptions for authentication-related errors.

It extends the base exception handling mechanism provided by `BaseAPIException`
to add a specific exception class for authentication scenarios.

The module can be used to raise exceptions when authentication errors occur,
providing clear and consistent error handling throughout the application.
"""

from core.base_exception import BaseAPIException


class AuthenticationException(BaseAPIException):
    """
    A custom exception class to handle authentication errors.

    Inherits from `BaseAPIException` and is used to represent errors
    related to failed authentication attempts, such as invalid credentials
    or unauthorized access.

    This class provides a consistent structure for managing
    authentication-related exceptions in the application.
    """

    ...
