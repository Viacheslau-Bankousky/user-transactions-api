"""
Module for handling user authentication and generating access tokens.

This module provides an endpoint for user login and access token
generation using FastAPI.
It integrates the `authenticate_user` function to verify the user's
credentials and generates a JWT token upon successful authentication.
The token is configured with a set expiration time defined in the
application constants.

Key features include:
- Login endpoint (`/token`) that accepts user credentials and returns
 a secure access token.
- Uses OAuth2 standard with password grant for user authentication flow
 (`OAuth2PasswordRequestForm`).
- Tokens are generated using the `create_access_token` utility,
containing payload information and an expiration time.

This module ensures secure and scalable token-based authentication for
the application.
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from authentication.access_tokens import create_access_token
from authentication.user_management import authenticate_user
from core.constants import ACCESS_TOKEN_EXPIRE_MINUTES
from models.users import User
from schemas.authentication import Token

router = APIRouter()


@router.post(
    "/token",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    description="Login for access token",
    response_description="Access token generated successfully",
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    Authenticate a user and return an access token for API authorization.

    Args:
        form_data (Annotated[OAuth2PasswordRequestForm, Depends]): The form
            data containing username and password.
            This is automatically handled by FastAPI's dependency injection.

    Returns:
        Token: A token object containing the access token and its type
        (e.g., Bearer token).
    """
    user: User = await authenticate_user(
        form_data.username, form_data.password
    )
    access_token_expires: timedelta = timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token: str = create_access_token(
        payload={"sub": user.name}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
