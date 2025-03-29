"""
Module for transaction request and response models.

This module defines two classes:
1. `RequestTransactionModel`: Used for validating and processing
 transaction requests.
2. `TransactionModel`: Represents the structure of a transaction
 in the system.

The models utilize Pydantic's validation features to enforce strong
type checking and ensure valid data during requests and responses.

Key features:
- **RequestValidation**:
    - Transaction amount validation ensuring it's positive.
    - Typed enumerations for currency, purpose, and status.
- **ResponseSerialization**:
    - Details of transaction entities, including metadata like creation
      timestamps.

This module is critical for consistent transaction data handling across
the application.
"""

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
    """
    Data model for transaction requests.

    Attributes:
        currency: The currency of the transaction (e.g., USD, EUR).
            Enforced as an enumeration from the `CurrencyEnum` class.
        amount: The transaction amount (must be a positive decimal value).
        purpose: The purpose of the transaction (e.g., refund, withdrawal).
            Enforced as an enumeration from the `TransactionPurposeEnum` class.
    """

    currency: CurrencyEnum
    amount: Decimal
    purpose: TransactionPurposeEnum

    @field_validator("amount")
    def validate_not_negative(cls, transaction_amount: Decimal) -> Decimal:
        """
        Ensure the transaction amount is not negative or zero.

        Args:
            transaction_amount: The value of the transaction amount
                being validated.

        Returns:
            The validated transaction amount.

        Raises:
            BadRequestDataException: If the transaction amount is less
                than or equal to 0, a 400 HTTP exception is triggered.
        """
        if transaction_amount <= 0:
            raise BadRequestDataException(
                message="Amount cannot be negative or zero",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return transaction_amount


class TransactionModel(BasePydanticModel):
    """
    Data model for transaction responses.

    Attributes:
        id: The unique identifier for the transaction (optional).
        user_id: The ID of the user associated with the transaction (optional).
        currency: The currency of the transaction. Enforced as an enumeration
            from the `CurrencyEnum` class (optional).
        amount: The transaction amount (optional). Represented as a float for
            flexible handling during serialization.
        status: The status of the transaction (e.g., pending, completed).
            Enforced as an enumeration from the `TransactionStatusEnum` class
                (optional).
        created: The timestamp indicating when the transaction was created
            (optional).
        purpose: The purpose of the transaction (e.g.,refund, withdrawal).
            Enforced as an enumeration from the `TransactionPurposeEnum`
                class (optional).
    """

    id: int | None = None
    user_id: int | None = None
    currency: CurrencyEnum | None = None
    amount: float | None = None
    status: TransactionStatusEnum | None = None
    created: datetime | None = None
    purpose: TransactionPurposeEnum | None = None
