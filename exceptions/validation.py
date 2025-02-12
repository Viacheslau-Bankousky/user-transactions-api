"""This module defines custom exceptions for handling specific error cases."""

from core.base_exception import BaseAPIException


class BadRequestDataException(BaseAPIException):
    """
    Exception raised for bad or invalid request data.

    This exception is a subclass of `BaseAPIException` and is specifically
    used to indicate that the client has sent a request with invalid data.
    It provides a consistent structure for handling such errors in the
    application.
    """

    ...
