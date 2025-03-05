from datetime import datetime
from typing import List

from pydantic import EmailStr, field_validator

from authentication.security import pwd_context
from core.pydantic_base import BasePydanticModel
from models.enums import UserStatusEnum
from schemas.user_balances import ResponseUserBalanceModel


class RequestUserModel(BasePydanticModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("name", "email", mode="before")
    def strip_spaces(cls, user_value: str) -> str:
        return user_value.strip()

    @field_validator("password", mode="before")
    def validate_password(cls, password: str) -> str:
        return pwd_context.hash(password)


class RequestUserUpdateModel(BasePydanticModel):
    email: EmailStr | None = None
    name: str | None = None
    status: UserStatusEnum | None = None


class UserModel(BasePydanticModel):
    id: int
    name: str
    email: str | None
    status: UserStatusEnum
    created: datetime


class ResponseUserModel(BasePydanticModel):
    id: int
    name: str
    email: str | None = None
    status: UserStatusEnum
    created: datetime
    balances: List[ResponseUserBalanceModel]
