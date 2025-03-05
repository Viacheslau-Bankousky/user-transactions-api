from datetime import datetime, timedelta, timezone
from typing import Dict

import jwt

from core.base_settings import settings
from core.constants import ALGORITHM

MINUTES_TO_EXPIRE: int = 15


def create_access_token(
    payload: Dict, expires_delta: timedelta | None = None
) -> str:
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
