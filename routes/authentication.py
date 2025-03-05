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
