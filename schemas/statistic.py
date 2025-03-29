"""
Module for defining response models for transaction statistics.

This module contains the `ResponseStatisticModel` class, which is used to
structure the response data for transaction and user statistics analysis.
It extends the `BasePydanticModel` to leverage Pydantic's features such as
data validation and serialization.

Key features:
- **Statistics by Date Range**: Includes fields to specify the start and
 end dates for the analyzed period.
- **User Statistics**: Tracks counts of registered users and those who made
 transactions (e.g., deposits, withdrawals).
- **Transaction Statistics**: Provides details on transaction counts and
 amounts, including rollback status.

The `ResponseStatisticModel` is typically used as a response model for APIs
that handle asynchronous transaction analysis and reporting.
"""

from datetime import date

from core.pydantic_base import BasePydanticModel


class ResponseStatisticModel(BasePydanticModel):
    """
    Data model for transaction statistics over a specific period.

    Attributes:
        start_date: The starting date of the analyzed period.
        end_date: The ending date of the analyzed period.
        registered_users_count: The total number of users registered during
            the period.
        registered_and_deposit_users_count: The number of users who registered
            and made at least one deposit during the period.
        registered_and_not_rollbacked_deposit_users_count: The number of users
            who registered and made at least one deposit that was not
            rolled back.
        not_rollbacked_deposit_amount: The total amount of deposits
            that were not rolled back.
        not_rollbacked_withdraw_amount: The total amount of withdrawals
            that were not rolled back.
        transactions_count: The total number of transactions during the period.
        not_rollbacked_transactions_count: The total number of transactions
            that were not rolled back.

    This class is designed for response purposes, helping to summarize key
    transaction and user behavior metrics during a specified time frame.
    """

    start_date: date
    end_date: date
    registered_users_count: int
    registered_and_deposit_users_count: int
    registered_and_not_rollbacked_deposit_users_count: int
    not_rollbacked_deposit_amount: str
    not_rollbacked_withdraw_amount: str
    transactions_count: int
    not_rollbacked_transactions_count: int
