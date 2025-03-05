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
from tests.utils.assert_checkers import check_transaction_response_assertation


@pytest.mark.asyncio
async def test_can_add_refund_transaction(
    overridden_dependency: AsyncGenerator, async_client: AsyncClient
) -> None:
    request_data: Dict[str, Any] = {
        "currency": CurrencyEnum.USD,
        "amount": 1000,
        "purpose": TransactionPurposeEnum.REFUND,
    }
    expected_user_id: int = 1
    expected_amount: Decimal = Decimal(1000)

    response = await async_client.post(
        url="users/1/transactions/refund",
        timeout=5,
        json=request_data,
    )
    response_data: Dict = response.json()

    check_transaction_response_assertation(
        response_data=response_data,
        expected_status=TransactionStatusEnum.PROCESSED,
        expected_amount=expected_amount,
        expected_user_id=expected_user_id,
        expected_currency=CurrencyEnum.USD,
        expected_purpose=TransactionPurposeEnum.REFUND,
    )


@pytest.mark.asyncio
async def test_can_add_deduct_transaction(
    overridden_dependency: AsyncGenerator, async_client: AsyncClient
) -> None:
    request_data: Dict[str, Any] = {
        "currency": CurrencyEnum.USD,
        "amount": 500,
        "purpose": TransactionPurposeEnum.WITHDRAWAL,
    }
    expected_amount: Decimal = Decimal(500)
    expected_user_id: int = 1

    response = await async_client.post(
        url="users/1/transactions/deduct",
        timeout=5,
        json=request_data,
    )
    response_data: Dict = response.json()

    check_transaction_response_assertation(
        response_data=response_data,
        expected_status=TransactionStatusEnum.PROCESSED,
        expected_amount=expected_amount,
        expected_user_id=expected_user_id,
        expected_currency=CurrencyEnum.USD,
        expected_purpose=TransactionPurposeEnum.WITHDRAWAL,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route, purpose",
    [
        (
            "users/1000/transactions/deduct",
            TransactionPurposeEnum.WITHDRAWAL,
        ),
        (
            "users/1000/transactions/refund",
            TransactionPurposeEnum.REFUND,
        ),
    ],
)
async def test_can_not_add_transaction_with_wrong_user_id(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
    route: str,
    purpose: TransactionPurposeEnum,
) -> None:
    request_data: Dict[str, Any] = {
        "currency": CurrencyEnum.USD,
        "amount": 200,
        "purpose": purpose,
    }

    response = await async_client.post(
        url=route,
        timeout=5,
        json=request_data,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert NOTHING_WAS_FOUND_MESSAGE in response_data.values()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route, purpose",
    [
        (
            "users/3/transactions/deduct",
            TransactionPurposeEnum.WITHDRAWAL,
        ),
        (
            "users/3/transactions/refund",
            TransactionPurposeEnum.REFUND,
        ),
    ],
)
async def test_can_not_add_transaction_to_blocked_user(
    async_client: AsyncClient,
    overridden_dependency: AsyncGenerator,
    route: str,
    purpose: TransactionPurposeEnum,
) -> None:
    request_data: Dict[str, Any] = {
        "currency": CurrencyEnum.USD,
        "amount": 200,
        "purpose": purpose,
    }
    expected_message: str = "User is blocked"

    response = await async_client.post(
        url=route,
        timeout=5,
        json=request_data,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert expected_message in response_data.values()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route, purpose",
    [
        (
            "users/1/transactions/deduct",
            TransactionPurposeEnum.WITHDRAWAL,
        ),
        (
            "users/1/transactions/refund",
            TransactionPurposeEnum.REFUND,
        ),
    ],
)
async def test_can_not_add_transaction_with_negative_amount(
    async_client: AsyncClient,
    overridden_dependency: AsyncGenerator,
    route: str,
    purpose: TransactionPurposeEnum,
) -> None:
    request_data: Dict[str, Any] = {
        "currency": CurrencyEnum.USD,
        "amount": -1,
        "purpose": purpose,
    }
    expected_message: str = "Amount cannot be negative or zero"

    response = await async_client.post(
        url=route,
        timeout=5,
        json=request_data,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert expected_message in response_data.values()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route, purpose",
    [
        (
            "users/1/transactions/deduct",
            TransactionPurposeEnum.WITHDRAWAL,
        ),
        (
            "users/1/transactions/refund",
            TransactionPurposeEnum.REFUND,
        ),
    ],
)
async def test_can_not_add_transaction_without_amount(
    async_client: AsyncClient,
    overridden_dependency: AsyncGenerator,
    route: str,
    purpose: TransactionPurposeEnum,
) -> None:
    request_data: Dict[str, Any] = {
        "currency": CurrencyEnum.USD,
        "purpose": purpose,
    }
    expected_message: str = "Field required"

    response = await async_client.post(
        url=route,
        timeout=5,
        json=request_data,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response_data["detail"][0]["msg"] == expected_message


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route, purpose",
    [
        (
            "users/1/transactions/deduct",
            TransactionPurposeEnum.WITHDRAWAL,
        ),
        (
            "users/1/transactions/refund",
            TransactionPurposeEnum.REFUND,
        ),
    ],
)
async def test_can_not_add_transaction_without_currency(
    async_client: AsyncClient,
    overridden_dependency: AsyncGenerator,
    route: str,
    purpose: TransactionPurposeEnum,
) -> None:
    request_data: Dict[str, Any] = {
        "amount": 500,
        "purpose": purpose,
    }
    expected_message: str = "Field required"

    response = await async_client.post(
        url=route,
        timeout=5,
        json=request_data,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response_data["detail"][0]["msg"] == expected_message


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route, purpose",
    [
        (
            "users/1/transactions/deduct",
            TransactionPurposeEnum.WITHDRAWAL,
        ),
        (
            "users/1/transactions/refund",
            TransactionPurposeEnum.REFUND,
        ),
    ],
)
async def test_can_not_add_transaction_with_wrong_currency(
    async_client: AsyncClient,
    overridden_dependency: AsyncGenerator,
    route: str,
    purpose: TransactionPurposeEnum,
) -> None:
    request_data: Dict[str, Any] = {
        "currency": "wrong_currency",
        "amount": 500,
        "purpose": purpose,
    }
    expected_message: str = (
        "Input should be 'USD', 'EUR', 'AUD', 'CAD',"
        " 'ARS', 'PLN', 'BTC', 'ETH', 'DOGE' or 'USDT'"
    )

    response = await async_client.post(
        url=route,
        timeout=5,
        json=request_data,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response_data["detail"][0]["msg"] == expected_message


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route",
    [
        "users/1/transactions/deduct",
        "users/1/transactions/refund",
    ],
)
async def test_can_not_add_transaction_without_purpose(
    async_client: AsyncClient,
    overridden_dependency: AsyncGenerator,
    route: str,
) -> None:
    request_data: Dict[str, Any] = {
        "currency": CurrencyEnum.USD,
        "amount": 500,
    }
    expected_message: str = "Field required"

    response = await async_client.post(
        url=route,
        timeout=5,
        json=request_data,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response_data["detail"][0]["msg"] == expected_message


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route",
    [
        "users/1/transactions/deduct",
        "users/1/transactions/refund",
    ],
)
async def test_can_not_add_transaction_with_wrong_purpose(
    async_client: AsyncClient,
    overridden_dependency: AsyncGenerator,
    route: str,
) -> None:
    request_data: Dict[str, Any] = {
        "currency": CurrencyEnum.USD,
        "amount": 500,
        "purpose": "wrong_purpose",
    }
    expected_message: str = "Input should be 'REFUND' or 'WITHDRAWAL'"

    response = await async_client.post(
        url=route,
        timeout=5,
        json=request_data,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response_data["detail"][0]["msg"] == expected_message


@pytest.mark.asyncio
async def test_can_not_add_deduct_transaction_to_empty_balance(
    async_client: AsyncClient,
    overridden_dependency: AsyncGenerator,
) -> None:
    request_data: Dict[str, Any] = {
        "currency": CurrencyEnum.USD,
        "amount": 500,
        "purpose": TransactionPurposeEnum.WITHDRAWAL,
    }
    expected_message: str = "Not enough balance"

    response = await async_client.post(
        url="users/2/transactions/deduct",
        timeout=5,
        json=request_data,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert expected_message in response_data.values()
