from typing import Any, Dict

import pytest
from fastapi import status
from httpx import AsyncClient

from models.enums import (
    CurrencyEnum,
    TransactionPurposeEnum,
    TransactionStatusEnum,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route",
    [
        "/transactions",
        "users/1/transactions",
        f"/transactions/{TransactionStatusEnum.PROCESSED}",
        f"/transactions/{TransactionStatusEnum.ROLL_BACKED}",
        f"users/1/transactions/{TransactionStatusEnum.PROCESSED}",
    ],
)
async def test_can_not_get_transactions_without_authentication(
    async_client: AsyncClient, route: str
) -> None:
    expected_message: str = "Not authenticated"

    response = await async_client.get(
        url=route,
        timeout=5,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert expected_message in response.json().values()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route", ["users/1/transactions/refund", "users/1/transactions/deduct"]
)
async def test_can_not_add_transactions_without_authentication(
    async_client: AsyncClient, route: str
) -> None:
    request_data: Dict[str, Any] = {
        "currency": CurrencyEnum.USD,
        "amount": 1000,
        "purpose": TransactionPurposeEnum.REFUND,
    }
    expected_message: str = "Not authenticated"

    response = await async_client.post(
        url=route,
        timeout=5,
        json=request_data,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert expected_message in response.json().values()


@pytest.mark.asyncio
async def test_can_not_rollback_transactions_without_authentication(
    async_client: AsyncClient
) -> None:
    expected_message: str = "Not authenticated"
    user_id: int = 1
    transaction_id: int = 1

    response = await async_client.patch(
        url=f"users/{user_id}/transactions/{transaction_id}",
        timeout=5,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert expected_message in response.json().values()
