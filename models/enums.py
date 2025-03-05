"""
This module defines enumerations for various constants used in the application.

The enums provide a structured and type-safe way to manage sets of related
values, such as currencies, user statuses, and transaction statuses.

Enumerations:
- `CurrencyEnum`: Lists supported currencies, including fiat currencies and
cryptocurrencies.
- `UserStatusEnum`: Represents the possible statuses of a user in the system.
- `TransactionStatusEnum`: Represents the possible statuses of a transaction
in the system.
"""

from enum import StrEnum


class CurrencyEnum(StrEnum):
    """
    Enumeration of supported currencies.

    This enum contains codes for both fiat currencies and cryptocurrencies.

    It ensures consistent reference throughout the application.

    Members:
        USD (str): United States Dollar (USD).
        EUR (str): Euro (EUR).
        AUD (str): Australian Dollar (AUD).
        CAD (str): Canadian Dollar (CAD).
        ARS (str): Argentine Peso (ARS).
        PLN (str): Polish Zloty (PLN).
        BTC (str): Bitcoin (BTC).
        ETH (str): Ethereum (ETH).
        DOGE (str): Doge-coin (DOGE).
        USDT (str): Tether (USDT).
    """

    USD = "USD"
    EUR = "EUR"
    AUD = "AUD"
    CAD = "CAD"
    ARS = "ARS"
    PLN = "PLN"
    BTC = "BTC"
    ETH = "ETH"
    DOGE = "DOGE"
    USDT = "USDT"


class UserStatusEnum(StrEnum):
    """
    Enumeration of user statuses.

    This enum defines possible states that a user can have in the system.

    Members:
        active (str): Indicates the user is active and permitted to use
            the system.
        blocked (str): Indicates the user is blocked and cannot use
            the system.
    """

    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"


class TransactionStatusEnum(StrEnum):
    """
    Enumeration of transaction statuses.

    This enum defines the possible states of a transaction in the system.

    Members:
        processed (str): Indicates the transaction has been successfully
            processed.
        roll_backed (str): Indicates the transaction has been rolled back.
    """

    PROCESSED = "PROCESSED"
    ROLL_BACKED = "ROLL_BACKED"


class TransactionPurposeEnum(StrEnum):
    REFUND = "REFUND"
    WITHDRAWAL = "WITHDRAWAL"
