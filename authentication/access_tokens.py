"""
This module provides functionality to generate and encode JSON Web Tokens.

The primary functionality of this module is handled by the
`create_access_token` function, which creates and encodes a JWT using
a given payload and optional expiration duration.
It utilizes the `jwt` library to create the token and ensures the token
is signed securely based on the application's settings.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict

import jwt

from core.base_settings import settings
from core.constants import ALGORITHM

MINUTES_TO_EXPIRE: int = 15


def create_access_token(
    payload: Dict, expires_delta: timedelta | None = None
) -> str:
    """
    Create a signed JSON Web Token (JWT) with an optional expiration time.

    This function generates a JWT by adding a payload and an expiration
    timestamp. If no custom expiration duration is provided, it defaults
    to `MINUTES_TO_EXPIRE`. The token is encoded using the application's
    `SECRET_KEY` and specified algorithm.

    Args:
        payload (Dict): The data to include in the token's payload. Must be a
            dictionary containing any custom key-value pairs.
        expires_delta (timedelta | None, optional): A custom expiration
            duration for the token. Defaults to `None`, in which case a
            standard expiration time of 15 minutes is applied.

    Returns:
        str: A string representing the encoded JWT, ready to be used for
            authentication or other secure operations.

    Notes:
        - The token includes the `exp` claim to specify the expiration time.
        - The encoding uses settings.SECRET_KEY as the signing key.
        - The algorithm used for signing the token is defined by `ALGORITHM`.
    """
    to_encode: Dict = payload.copy()
    if expires_delta:
        expire: datetime = datetime.now(timezone.utc) + expires_delta
    else:
        expire: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=MINUTES_TO_EXPIRE
        )
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(
        to_encode, key=settings.SECRET_KEY, algorithm=ALGORITHM
    )

    return encoded_jwt
