from datetime import datetime
from typing import List

from pydantic import EmailStr, field_validator
from pydantic.v1 import root_validator

from core.pydantic_base import BasePydanticModel
from models.enums import CurrencyEnum, UserStatusEnum


class RequestUserModel(BasePydanticModel):
    name: str
    email: EmailStr

    @field_validator("name", "email", mode="before")
    def strip_spaces(cls, user_value: str) -> str:
        return user_value.strip()


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


class UserBalanceModel(BasePydanticModel):
    id: int | None = None
    user_id: int | None = None
    currency: CurrencyEnum | None = None
    amount: float | None = None

    @root_validator(pre=True)
    def validate_not_negative(self, user_data):
        if "amount" in user_data and user_data.get("amount"):
            if user_data["amount"] < 0:
                raise ValueError("Amount cannot be negative")

        return user_data

class ResponseUserBalanceModel(BasePydanticModel):
    currency: CurrencyEnum | None = None
    amount: float | None = None


class ResponseUserModel(BasePydanticModel):
    id: int
    name: str
    email: str | None = None
    status: UserStatusEnum
    created: datetime
    balances: List[ResponseUserBalanceModel]
