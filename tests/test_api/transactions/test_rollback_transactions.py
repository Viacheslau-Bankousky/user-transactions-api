from decimal import Decimal
from typing import Any, AsyncGenerator, Dict

import pytest
from fastapi import status
from httpx import AsyncClient

from core.constants import NOTHING_WAS_FOUND_MESSAGE
from models.enums import (
    CurrencyEnum,
    TransactionPurposeEnum,
    TransactionStatusEnum,
)
from tests.utils.assert_checkers import assert_transaction_response


@pytest.mark.asyncio
async def test_can_rollback_refund_transaction(
    async_client: AsyncClient,
    overridden_dependency: AsyncGenerator,
) -> None:
    amount = Decimal(1000)
    user_id = transaction_id = 1

    response = await async_client.patch(
        url=f"users/{user_id}/transactions/{transaction_id}",
        timeout=5,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert_transaction_response(
        response_data=response_data,
        expected_status=TransactionStatusEnum.ROLL_BACKED,
        expected_amount=amount,
        expected_user_id=user_id,
        expected_currency=CurrencyEnum.USD,
        expected_purpose=TransactionPurposeEnum.REFUND,
    )


@pytest.mark.asyncio
async def test_can_rollback_deduct_transaction(
    overridden_dependency: AsyncGenerator, async_client: AsyncClient
) -> None:
    request_data: Dict[str, Any] = {
        "currency": CurrencyEnum.USD,
        "amount": 1000,
        "purpose": TransactionPurposeEnum.REFUND,
    }
    amount: Decimal = Decimal(1000)
    user_id: int = 1

    deduct_response = await async_client.post(
        url=f"users/{user_id}/transactions/deduct",
        timeout=5,
        json=request_data,
    )
    rollback_response = await async_client.patch(
        url=f"users/{user_id}/transactions/{deduct_response.json()['id']}",
        timeout=5,
    )
    response_data: Dict = rollback_response.json()

    assert rollback_response.status_code == status.HTTP_200_OK
    assert_transaction_response(
        response_data=response_data,
        expected_status=TransactionStatusEnum.ROLL_BACKED,
        expected_amount=amount,
        expected_user_id=user_id,
        expected_currency=CurrencyEnum.USD,
        expected_purpose=TransactionPurposeEnum.REFUND,
    )


@pytest.mark.asyncio
async def test_can_not_rollback_transaction_with_wrong_user_id(
    overridden_dependency: AsyncGenerator, async_client: AsyncClient
) -> None:
    wrong_user_id: int = 1000
    transaction_id: int = 1

    response = await async_client.patch(
        url=f"users/{wrong_user_id}/transactions/{transaction_id}",
        timeout=5,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert NOTHING_WAS_FOUND_MESSAGE in response_data.values()


@pytest.mark.asyncio
async def test_can_not_rollback_transaction_with_wrong_transaction_id(
    overridden_dependency: AsyncGenerator, async_client: AsyncClient
) -> None:
    wrong_transaction_id: int = 1000
    user_id: int = 1

    response = await async_client.patch(
        url=f"users/{user_id}/transactions/{wrong_transaction_id}",
        timeout=5,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert NOTHING_WAS_FOUND_MESSAGE in response_data.values()


@pytest.mark.asyncio
async def test_can_not_rollback_transaction_of_blocked_user(
    overridden_dependency: AsyncGenerator, async_client: AsyncClient
) -> None:
    blocked_user_id: int = 3
    transaction_id: int = 2
    expected_message: str = "User is blocked"

    response = await async_client.patch(
        url=f"users/{blocked_user_id}/transactions/{transaction_id}",
        timeout=5,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert expected_message in response_data.values()
