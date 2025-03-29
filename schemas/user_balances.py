"""
Module for user balance response model.

This module defines the `ResponseUserBalanceModel` class, which is used
to structure responses regarding a user's balance details.
It extends the `BasePydanticModel` to provide robust Pydantic features
such as data validation and serialization.

Key features:
- **User Balance Data**: Includes attributes for balance amount and
 currency type.
- **Optional Attributes**: Allows flexibility with optional fields
 for cases where some data might not be available.

This model is designed to standardize the representation of user
balances in responses, ensuring consistency across the application.
"""

from decimal import Decimal

from core.pydantic_base import BasePydanticModel
from models.enums import CurrencyEnum


class ResponseUserBalanceModel(BasePydanticModel):
    """
    Data model for user balance responses.

    Attributes:
        currency: The type of currency for the user's balance (e.g., USD, EUR).
            Enforced as an enumeration from the `CurrencyEnum` class.
            This field is optional.
        amount: The balance amount in the specified currency.
            Represented as a decimal value to maintain precision
            for financial data.
            This field is also optional.
    """

    currency: CurrencyEnum | None = None
    amount: Decimal | None = None
