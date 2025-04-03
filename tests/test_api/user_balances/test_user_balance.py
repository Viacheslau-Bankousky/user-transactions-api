"""
Module for Testing User Balance Updates via Transactions.

This module contains test cases designed to validate the correct behavior
of user balance updates when transactions are created, deducted, and rolled
back.

Key Features:
- **Balance Increases**:
  - Verify that user balances are correctly increased after refund
   transactions.
- **Balance Decreases**:
  - Ensure user balances are decreased correctly after deduct (withdrawal)
   transactions.
- **Balance Restoration**:
  - Validate that balances are restored correctly after rolling back
   transactions.

Dependencies:
- `pytest`: For defining and running the test cases.
- `pytest.mark.asyncio`: For executing asynchronous test functions.
- `httpx.AsyncClient`: For making HTTP requests to simulate user
transactions.
- `models.enums`: Enumerations for transaction attributes like currency
 and purpose.
- `models.users.UserBalance`: Represents the user's balance, used for
 verification.
- `repositories.users_balances.get_user_balance_for_currency`: Function
 to fetch user balance for a given currency.
"""

from decimal import Decimal
from typing import Any, AsyncGenerator, Dict

import pytest
from httpx import AsyncClient

from models.enums import (
    CurrencyEnum,
    TransactionPurposeEnum,
)
from models.users import UserBalance
from repositories.users_balances import get_user_balance_for_currency


@pytest.mark.asyncio
async def test_can_increase_balance_after_refund_transaction(
    async_client: AsyncClient,
    overridden_dependency: AsyncGenerator,
    initial_user_balance: UserBalance,
    async_db_session: AsyncGenerator,
) -> None:
    """
    Test balance increase after a refund transaction.

    Verifies that the user's balance is increased correctly when a refund
    transaction is created for a specific currency.

    Args:
        async_client (AsyncClient): Asynchronous HTTP client for making
            API requests.
        overridden_dependency (AsyncGenerator): Dependency injection
            to mock services.
        initial_user_balance (UserBalance): The user's balance before
            the transaction.
        async_db_session (AsyncGenerator): Database session for querying
            user balances.
    """
    initial_balance: Decimal = Decimal(0)
    increased_balance: Decimal = Decimal(500)
    user_id: int = 2
    request_data: Dict[str, Any] = {
        "currency": CurrencyEnum.USD,
        "amount": 500,
        "purpose": TransactionPurposeEnum.REFUND,
    }

    await async_client.post(
        url=f"users/{user_id}/transactions/refund",
        timeout=5,
        json=request_data,
    )
    updated_user_balance: UserBalance = await get_user_balance_for_currency(
        user_id=user_id, currency=CurrencyEnum.USD, session=async_db_session
    )

    assert initial_user_balance.amount == initial_balance
    assert updated_user_balance.amount == increased_balance


@pytest.mark.asyncio
async def test_can_decrease_balance_after_deduct_transaction(
    async_client: AsyncClient,
    overridden_dependency: AsyncGenerator,
    initial_user_balance: UserBalance,
    async_db_session: AsyncGenerator,
) -> None:
    """
    Test balance decrease after a deduct (withdrawal) transaction.

    Simulates a refund to increase the initial balance, followed by a deduct
    transaction to verify balance decrease to its initial value.

    Args:
        async_client (AsyncClient): Asynchronous HTTP client for making API
            requests.
        overridden_dependency (AsyncGenerator): Dependency injection to mock
            services.
        initial_user_balance (UserBalance): The user's balance before the
            transactions.
        async_db_session (AsyncGenerator): Database session for querying
            user balances.
    """
    initial_balance: Decimal = Decimal(0)
    decreased_balance: Decimal = Decimal(0)
    user_id: int = 2
    refund_request_data: Dict[str, Any] = {
        "currency": CurrencyEnum.USD,
        "amount": 500,
        "purpose": TransactionPurposeEnum.REFUND,
    }
    withdrawal_request_data: Dict[str, Any] = {
        "currency": CurrencyEnum.USD,
        "amount": 500,
        "purpose": TransactionPurposeEnum.WITHDRAWAL,
    }

    await async_client.post(
        url=f"users/{user_id}/transactions/refund",
        timeout=5,
        json=refund_request_data,
    )
    await async_client.post(
        url=f"users/{user_id}/transactions/deduct",
        timeout=5,
        json=withdrawal_request_data,
    )
    updated_user_balance: UserBalance = await get_user_balance_for_currency(
        user_id=user_id, currency=CurrencyEnum.USD, session=async_db_session
    )

    assert initial_user_balance.amount == initial_balance
    assert updated_user_balance.amount == decreased_balance


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "transaction_purpose",
    [
        TransactionPurposeEnum.REFUND,
        TransactionPurposeEnum.WITHDRAWAL,
    ],
)
async def test_can_restore_balance_after_rollback_transaction(
    async_client: AsyncClient,
    overridden_dependency: AsyncGenerator,
    initial_user_balance: UserBalance,
    async_db_session: AsyncGenerator,
    transaction_purpose: TransactionPurposeEnum,
) -> None:
    """
    Test restoring balance after a transaction rollback.

    Validates that the user's balance is restored to its original value
    when a transaction, either refund or withdrawal, is rolled back.

    Args:
        async_client (AsyncClient): Asynchronous HTTP client for making API
            requests.
        overridden_dependency (AsyncGenerator): Dependency injection to mock
            services.
        initial_user_balance (UserBalance): The user's balance before the
            transactions.
        async_db_session (AsyncGenerator): Database session for querying
            user balances.
        transaction_purpose (TransactionPurposeEnum): Type of transaction
            (REFUND or WITHDRAWAL).
    """
    balance: Decimal = Decimal(0)
    user_id: int = 1
    request_data: Dict[str, Any] = {
        "currency": CurrencyEnum.USD,
        "amount": 5000,
        "purpose": transaction_purpose,
    }

    refund_response = await async_client.post(
        url=f"users/{user_id}/transactions/refund",
        timeout=5,
        json=request_data,
    )
    await async_client.patch(
        url=f"users/{user_id}/transactions/{refund_response.json()['id']}",
        timeout=5,
    )
    decreased_user_balance: UserBalance = await get_user_balance_for_currency(
        user_id=user_id, currency=CurrencyEnum.USD, session=async_db_session
    )

    assert initial_user_balance.amount == balance
    assert decreased_user_balance.amount == balance
