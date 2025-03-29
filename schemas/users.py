"""
Module for user-related data models.

This module defines several data models used for handling user-related
information, requests, and responses.
These models extend the `BasePydanticModel` to provide robust data
validation, serialization, and consistency across the application.

Key features:
- **Request Models**: Define the structure for incoming user-related
 data, including user creation and update operations.
- **Response Models**: Standardize the structure of user-related data
 returned in API responses.
- **Utility Validators**: Provide field-level validation such as string
 stripping and password hashing for secure and clean data processing.

Classes:
- **RequestUserModel**: Represents the structure for creating a new user,
  including validation for username, email, and password.
- **RequestUserUpdateModel**: Represents the structure for updating user
 information, with optional attributes for flexibility.
- **UserModel**: Serves as an internal model representing the user entity.
- **ResponseUserModel**: Structures the user-related data returned in API
 responses, including user balances.

Dependencies:
- This module imports the `BasePydanticModel` class for model creation,
  validators from `pydantic` for data preprocessing and validation,
  and custom utilities such as `pwd_context` for password hashing.
"""

from datetime import datetime
from typing import List

from pydantic import EmailStr, field_validator

from authentication.security import pwd_context
from core.pydantic_base import BasePydanticModel
from models.enums import UserStatusEnum
from schemas.user_balances import ResponseUserBalanceModel


class RequestUserModel(BasePydanticModel):
    """
    Data model for user creation requests.

    Attrs:
        name: The name of the user. Whitespaces are trimmed during validation.
        email: The user's email address. Must be a valid email format.
        password: The user's password. It undergoes hashing for secure storage.
    """

    name: str
    email: EmailStr
    password: str

    @field_validator("name", "email", mode="before")
    def strip_spaces(cls, user_value: str) -> str:
        """
        Validator to trim leading and trailing spaces from name and email fields.

        Args:
            user_value: Input provided by the user for name or email.

        Returns:
            The trimmed string.
        """
        return user_value.strip()

    @field_validator("password", mode="before")
    def validate_password(cls, password: str) -> str:
        """
        Validator to hash the user's password for secure storage.

        Args:
            password: The plaintext password provided by the user.

        Returns:
            The hashed password.
        """
        return pwd_context.hash(password)


class RequestUserUpdateModel(BasePydanticModel):
    """
    Data model for user update requests.

    Attrs:
        email: The updated email address. Must be in a valid email format.
            This field is optional.
        name: The updated name of the user. This field is optional.
        status: The updated status of the user. Enforced as an enumeration
            of type `UserStatusEnum`. This field is optional.
    """

    email: EmailStr | None = None
    name: str | None = None
    status: UserStatusEnum | None = None


class UserModel(BasePydanticModel):
    """
    Internal data model for user information.

    Attrs:
        id: The unique identifier of the user.
        name: The name of the user.
        email: The email address of the user.
        status: Current status of the user.
        created: The timestamp when the user was created.
    """

    id: int
    name: str
    email: str | None
    status: UserStatusEnum
    created: datetime


class ResponseUserModel(BasePydanticModel):
    """
    Data model for user information in API responses.

    Attrs:
        id: The unique identifier of the user.
        name: The name of the user.
        email: The email address associated with the user. Defaults to `None`.
        status: Current status of the user. Derived from `UserStatusEnum`.
        created: The timestamp indicating when the user was created.
        balances: A list of balance details for the user. Structured
            as instances of `ResponseUserBalanceModel`.
    """

    id: int
    name: str
    email: str | None = None
    status: UserStatusEnum
    created: datetime
    balances: List[ResponseUserBalanceModel]
