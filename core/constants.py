"""
Module containing default constants used across the application.

This module defines default values and messages for reuse in various parts
of the application to ensure consistency.

Attributes:
    PRECISION (int): The precision used for decimal values.
    SCALE (int): The scale used for decimal values.
    NOTHING_WAS_FOUND_MESSAGE (str): A default message indicating that
    no results were found.
    USER_DOES_NOT_EXISTS (str): A default message indicating that a user
    does not exist.
    ALGORITHM (str): The algorithm used for generating JWT tokens.
    ACCESS_TOKEN_EXPIRE_MINUTES (int): The number of minutes after which
    an access token expires.
"""

PRECISION: int = 18
SCALE: int = 2
NOTHING_WAS_FOUND_MESSAGE: str = "Nothing was found"
USER_DOES_NOT_EXISTS: str = "User does not exist"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
