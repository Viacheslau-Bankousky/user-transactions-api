"""
Module for Testing Transaction Addition in Different Scenarios.

This module contains test cases that validate the behavior of
transaction-related API endpoints when adding refund or deduction
transactions under various scenarios. It ensures that the correct
HTTP responses, error codes, and messages are returned, depending
on the input parameters and conditions.

Key Features:
- **Happy Paths**:
  - Tests successful addition of refund and deduction transactions.
- **Negative Scenarios**:
  - Tests adding transactions with invalid user IDs.
  - Verifies correct handling when the user is blocked.
  - Tests transactions with invalid or missing parameters (e.g., negative
    amounts, invalid currencies, missing fields).
  - Confirms errors for users with insufficient balance.

Dependencies:
- `pytest`: For writing and running test cases.
- `pytest.mark.asyncio`: For asynchronous tests.
- `pytest.mark.parametrize`: For parameterizing test cases.
- `fastapi.status`: For HTTP status codes.
- `httpx.AsyncClient`: For making HTTP requests to the test server.
- `core.constants.NOTHING_WAS_FOUND_MESSAGE`: To assert appropriate
 error messages.
- `models.enums`: Enumerations for transaction properties
(e.g., currency, purpose, status).
- `tests.utils.assert_checkers.assert_transaction_response`:
    Helper function for asserting expected response fields.

Examples:
Each test simulates an API request to add a transaction, either succeeding
 or failing as the scenario dictates.
"""

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
async def test_can_add_refund_transaction(
    overridden_dependency: AsyncGenerator, async_client: AsyncClient
) -> None:
    """
    Test successfully adding a refund transaction.

    This test verifies that a refund transaction can be added for a valid user
    and that the response contains the expected values for the processed
    transaction.

    Args:
        overridden_dependency (AsyncGenerator): A testing dependency for
            mocking or overriding.
        async_client (AsyncClient): An asynchronous HTTP client for sending
            requests.
    """
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

    assert_transaction_response(
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
    """
    Test successfully adding a deduct transaction.

    This test verifies that a deduction (withdrawal) transaction can be added
    for a valid user and checks the response for expected details.

    Args:
        overridden_dependency (AsyncGenerator): A testing dependency for
            mocking or overriding.
        async_client (AsyncClient): An asynchronous HTTP client for
            sending requests.

    """
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

    assert_transaction_response(
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
    """
    Test adding a transaction for a nonexistent user.

    This test verifies that the API returns a 404 response when attempting to
    add a refund or deduction transaction for a user ID that does not exist.

    Args:
        overridden_dependency (AsyncGenerator): A testing dependency for
            mocking or overriding.
        async_client (AsyncClient): An asynchronous HTTP client for sending
            requests.
        route (str): API endpoint for the transaction request.
        purpose (TransactionPurposeEnum): Type of transaction
            (e.g., REFUND, WITHDRAWAL).
    """
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
    """
    Test adding a transaction for a blocked user.

    This test verifies that the API returns a 403 response when attempting to
    add a refund or deduction transaction for a user who is blocked.

    Args:
        async_client (AsyncClient): An asynchronous HTTP client for sending
            requests.
        overridden_dependency (AsyncGenerator): A testing dependency for
            mocking or overriding.
        route (str): API endpoint for the transaction request.
        purpose (TransactionPurposeEnum): Type of transaction
            (e.g., REFUND, WITHDRAWAL).
    """
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
    """
    Test adding a transaction with a negative amount.

    This test validates that the API rejects requests containing
    a negative or zero transaction amount. The proper error message
    is asserted in the response.

    Args:
        async_client (AsyncClient): An asynchronous HTTP client for
            sending requests.
        overridden_dependency (AsyncGenerator): A testing dependency
            for mocking or overriding.
        route (str): API endpoint for the transaction request.
        purpose (TransactionPurposeEnum): Type of transaction
            (e.g., REFUND, WITHDRAWAL).
    """
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
    """
    Test adding a transaction without specifying an amount.

    This test verifies that the API rejects requests where the transaction
    amount is missing and returns the appropriate error message.

    Args:
        async_client (AsyncClient): An asynchronous HTTP client for sending
            requests.
        overridden_dependency (AsyncGenerator): A testing dependency for
            mocking or overriding.
        route (str): API endpoint for the transaction request.
        purpose (TransactionPurposeEnum): Type of transaction
            (e.g., REFUND, WITHDRAWAL).
    """
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
    """
    Test adding a transaction without specifying a currency.

    This test ensures that requests missing the `currency` field are
    rejected by the API with the appropriate validation error message.

    Args:
        async_client (AsyncClient): An asynchronous HTTP client for
            sending requests.
        overridden_dependency (AsyncGenerator): A testing dependency
            for mocking or overriding.
        route (str): API endpoint for the transaction request.
        purpose (TransactionPurposeEnum): Type of transaction
            (e.g., REFUND, WITHDRAWAL).
    """
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
    """
    Test adding a transaction with an invalid currency.

    This test validates that the API rejects requests with unsupported
    `currency` values and returns the appropriate validation error message.

    Args:
        async_client (AsyncClient): An asynchronous HTTP client for sending
            requests.
        overridden_dependency (AsyncGenerator): A testing dependency for
            mocking or overriding.
        route (str): API endpoint for the transaction request.
        purpose (TransactionPurposeEnum): Type of transaction
            (e.g., REFUND, WITHDRAWAL).
    """
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
    """
    Test adding a transaction without specifying a purpose.

    This test ensures that requests missing the `purpose` field are rejected
    by the API and the appropriate validation error is returned.

    Args:
        async_client (AsyncClient): An asynchronous HTTP client for sending
            requests.
        overridden_dependency (AsyncGenerator): A testing dependency for
            mocking or overriding.
        route (str): API endpoint for the transaction request.
    """
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
    """
    Test adding a transaction with an invalid purpose.

    This test validates that the API rejects transactions with unsupported
    `purpose` values and returns the appropriate validation error message.

    Args:
        async_client (AsyncClient): An asynchronous HTTP client for sending
            requests.
        overridden_dependency (AsyncGenerator): A testing dependency for
            mocking or overriding.
        route (str): API endpoint for the transaction request.
    """
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
    """
    Test adding a debit transaction to a user with an insufficient balance.

    This test ensures that the API rejects requests to deduct amounts when the
    user's balance is insufficient to cover the transaction.

    Args:
        async_client (AsyncClient): An asynchronous HTTP client for sending
            requests.
        overridden_dependency (AsyncGenerator): A testing dependency for
            mocking or overriding.
    """
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
