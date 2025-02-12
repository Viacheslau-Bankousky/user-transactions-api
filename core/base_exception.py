"""
A module for defining a custom exception class for FastAPI-based application.

It is used for better customization of exceptions with a
human-readable message and HTTP status code, making error management more
consistent and structured.
"""

from fastapi.exceptions import HTTPException


class BaseAPIException(HTTPException):
    """
    A base class for defining custom API exceptions in FastAPI applications.

    This class extends FastAPI's `HTTPException` by adding a direct way to
    set a detailed error message and HTTP status code.
    It simplifies how application-level exceptions can be raised and adds
    support for better string representation of the exception.
    """

    def __init__(self, message: str, status_code: int) -> None:
        """
        Initialize the BaseAPIException with an error message and status code.

        Args:
            message (str): A short description of the error.
            status_code (int): The HTTP status code associated with the error.
        """
        super().__init__(status_code=status_code, detail=message)
        self.message = message
        self.status_code = status_code

    def __str__(self) -> str:
        """
        Return a string representation of the exception.

        Returns:
            str: A string in the format `Error <status_code>: <message>`.
        """
        return f"Error {self.status_code}: {self.message}"
