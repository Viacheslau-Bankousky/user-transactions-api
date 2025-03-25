"""
This module provides authentication utilities.

The primary functionalities include:
- Authentication of a user based on username and password.
- Validation of a JSON Web Token (JWT) to ensure the user has a valid
 access token.

It utilizes FastAPI's dependency injection with OAuth2 for token handling
 and the `jwt` library for token decoding and validation.
Custom exceptions are raised for authentication-related failures, such
as invalid credentials or invalid tokens.
"""
from typing import Annotated

import jwt
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from authentication.security import verify_password
from core.base_settings import settings
from core.constants import ALGORITHM
from core.database import get_session
from exceptions.authentication import AuthenticationException
from models.users import User
from repositories.users import take_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_user(username: str, password: str) -> User:
    """
    Authenticate a user by validating their username and password.

    This function queries the database for a user with the provided username,
    and then verifies that the provided password matches the stored hashed
    password.
    If the user does not exist or the password is incorrect, the function
    raises an `AuthenticationException`.

    Args:
        username (str): The username of the user attempting to authenticate.
        password (str): The plain text password provided for authentication.

    Returns:
        User: An instance of the authenticated `User` model.

    Raises:
        AuthenticationException: If the username is not found in the database
            or the password does not match.
    """
    async with get_session() as session:
        user: User | None = await take_user(session=session, name=username)
    if not user:
        raise AuthenticationException(
            message="Invalid username",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    if not verify_password(
        plain_password=password, hashed_password=user.password
    ):
        raise AuthenticationException(
            message="Invalid password",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return user


def check_user_has_token(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> bool:
    """
    Validate a user's access token to ensure it is correct and unexpired.

    This function decodes the provided JWT using the application's secret key
    and checks its validity. If the token is invalid, it raises an
        AuthenticationException`.

    Args:
        token (Annotated[str, Depends(oauth2_scheme)]): The access token to
            validate, obtained via FastAPI's OAuth2 dependency pipeline.

    Returns:
        bool: True if the token is valid.

    Raises:
        AuthenticationException: If the token is invalid or cannot be decoded.
    """
    try:
        jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return True
    except InvalidTokenError:
        raise AuthenticationException(
            message="Invalid token", status_code=status.HTTP_401_UNAUTHORIZED
        )
