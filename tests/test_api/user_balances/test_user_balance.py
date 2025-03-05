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
):
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
):
    initial_balance = decreased_balance = Decimal(0)
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
):
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
