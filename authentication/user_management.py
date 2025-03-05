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


async def authenticate_user(username: str, password: str):
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


def check_user_has_token(token: Annotated[str, Depends(oauth2_scheme)]) -> bool:
    try:
        jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return True
    except InvalidTokenError:
        raise AuthenticationException(
            message="Invalid token", status_code=status.HTTP_401_UNAUTHORIZED
        )
