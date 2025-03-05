from decimal import Decimal

from core.pydantic_base import BasePydanticModel
from models.enums import CurrencyEnum


class ResponseUserBalanceModel(BasePydanticModel):
    currency: CurrencyEnum | None = None
    amount: Decimal | None = None
