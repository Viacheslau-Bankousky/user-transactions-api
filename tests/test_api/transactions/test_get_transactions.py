from decimal import Decimal
from typing import AsyncGenerator, Dict, List

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
async def test_can_get_all_transactions(
    overridden_dependency: AsyncGenerator, async_client: AsyncClient
) -> None:
    expected_amount: Decimal = Decimal(1000)
    first_user_id: int = 1
    third_user_id: int = 3

    response = await async_client.get(
        url="/transactions",
        timeout=5,
    )
    response_data: List[Dict] = response.json()

    assert response.status_code == status.HTTP_200_OK
    for index, transaction in enumerate(response_data):
        assert_transaction_response(
            response_data=transaction,
            expected_status=TransactionStatusEnum.PROCESSED,
            expected_amount=expected_amount,
            expected_user_id=first_user_id if index == 0 else third_user_id,
            expected_currency=CurrencyEnum.USD,
            expected_purpose=TransactionPurposeEnum.REFUND,
        )


@pytest.mark.asyncio
async def test_can_get_transactions_by_user_id(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    user_id = expected_user_id = 1
    expected_amount: Decimal = Decimal(1000)

    response = await async_client.get(
        url=f"users/{user_id}/transactions",
        timeout=5,
    )
    response_data: List[Dict] = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert_transaction_response(
        response_data=response_data[0],
        expected_status=TransactionStatusEnum.PROCESSED,
        expected_amount=expected_amount,
        expected_user_id=expected_user_id,
        expected_currency=CurrencyEnum.USD,
        expected_purpose=TransactionPurposeEnum.REFUND,
    )


@pytest.mark.asyncio
async def test_can_not_get_transactions_with_wrong_user_id(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    wrong_user_id: int = 1000

    response = await async_client.get(
        url=f"users/{wrong_user_id}/transactions",
        timeout=5,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert NOTHING_WAS_FOUND_MESSAGE in response_data.values()


@pytest.mark.asyncio
async def test_can_get_processed_transactions(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    transaction_status: str = TransactionStatusEnum.PROCESSED
    expected_amount: Decimal = Decimal(1000)
    first_user_id: int = 1
    third_user_id: int = 3

    response = await async_client.get(
        url=f"/transactions/{transaction_status}",
        timeout=5,
    )
    response_data: List[Dict] = response.json()

    assert response.status_code == status.HTTP_200_OK
    for index, transaction in enumerate(response_data):
        assert_transaction_response(
            response_data=transaction,
            expected_status=TransactionStatusEnum.PROCESSED,
            expected_amount=expected_amount,
            expected_user_id=first_user_id if index == 0 else third_user_id,
            expected_currency=CurrencyEnum.USD,
            expected_purpose=TransactionPurposeEnum.REFUND,
        )


@pytest.mark.asyncio
async def test_can_get_rollbacked_transactions(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    transaction_status: str = TransactionStatusEnum.ROLL_BACKED
    expected_amount: Decimal = Decimal(1000)
    expected_user_id: int = 1

    await async_client.patch(
        url="users/1/transactions/1",
    )
    response = await async_client.get(
        url=f"/transactions/{transaction_status}",
        timeout=5,
    )
    response_data: List[Dict] = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert_transaction_response(
        response_data=response_data[0],
        expected_status=TransactionStatusEnum.ROLL_BACKED,
        expected_amount=expected_amount,
        expected_user_id=expected_user_id,
        expected_currency=CurrencyEnum.USD,
        expected_purpose=TransactionPurposeEnum.REFUND,
    )


@pytest.mark.asyncio
async def test_can_not_get_transactions_with_wrong_status(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    wrong_transaction_status: str = "wrong_status"
    expected_message: str = "Invalid status"

    response = await async_client.get(
        url=f"/transactions/{wrong_transaction_status}",
        timeout=5,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert expected_message in response_data.values()


@pytest.mark.asyncio
async def test_can_get_transactions_by_user_id_and_status(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    user_id = expected_user_id = 1
    transaction_status: str = TransactionStatusEnum.PROCESSED
    expected_amount: Decimal = Decimal(1000)

    response = await async_client.get(
        url=f"users/{user_id}/transactions/{transaction_status}",
        timeout=5,
    )
    response_data: List[Dict] = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert_transaction_response(
        response_data=response_data[0],
        expected_status=TransactionStatusEnum.PROCESSED,
        expected_amount=expected_amount,
        expected_user_id=expected_user_id,
        expected_currency=CurrencyEnum.USD,
        expected_purpose=TransactionPurposeEnum.REFUND,
    )


@pytest.mark.asyncio
async def test_can_not_get_user_transactions_with_wrong_status(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    user_id: int = 1
    wrong_transaction_status: str = "wrong_status"
    expected_message: str = "Invalid status"

    response = await async_client.get(
        url=f"users/{user_id}/transactions/{wrong_transaction_status}",
        timeout=5,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert expected_message in response_data.values()


@pytest.mark.asyncio
async def test_can_not_get_user_transactions_with_wrong_user_id(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    wrong_user_id: int = 1000
    transaction_status: str = TransactionStatusEnum.PROCESSED

    response = await async_client.get(
        url=f"users/{wrong_user_id}/transactions/{transaction_status}",
        timeout=5,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert NOTHING_WAS_FOUND_MESSAGE in response_data.values()
