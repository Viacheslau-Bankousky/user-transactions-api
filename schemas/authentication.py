"""
Module for handling authentication tokens.

This module defines the `Token` class that represents the structure
of tokens used for authentication purposes in the system.
It extends the `BasePydanticModel` class to provide additional
Pydantic capabilities such as validation, serialization, and type safety.

Key features:
- **Access Token**: Represents the token value used for authentication.
- **Token Type**: Specifies the type of the token, typically "Bearer".

This module centralizes the token structure to ensure consistency throughout
the application wherever tokens are processed or validated.
"""

from core.pydantic_base import BasePydanticModel


class Token(BasePydanticModel):
    """
    Representation of an authentication token.

    Attributes:
        access_token: The token string used for authenticating requests.
        token_type: The type of the token, typically set as "Bearer".

    This class is designed to be easily integrated with FastAPI and other
    components for validation and response serialization.
    """

    access_token: str
    token_type: str
