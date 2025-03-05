from datetime import datetime
from decimal import Decimal

from fastapi import status
from pydantic import field_validator

from core.pydantic_base import BasePydanticModel
from exceptions.validation import BadRequestDataException
from models.enums import (
    CurrencyEnum,
    TransactionPurposeEnum,
    TransactionStatusEnum,
)


class RequestTransactionModel(BasePydanticModel):
    currency: CurrencyEnum
    amount: Decimal
    purpose: TransactionPurposeEnum

    @field_validator("amount")
    def validate_not_negative(cls, transaction_amount: Decimal) -> Decimal:
        if transaction_amount <= 0:
            raise BadRequestDataException(
                message="Amount cannot be negative or zero",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return transaction_amount


class TransactionModel(BasePydanticModel):
    id: int | None = None
    user_id: int | None = None
    currency: CurrencyEnum | None = None
    amount: float | None = None
    status: TransactionStatusEnum | None = None
    created: datetime | None = None
    purpose: TransactionPurposeEnum | None = None
