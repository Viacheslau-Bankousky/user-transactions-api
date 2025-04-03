"""
Module for Testing Transaction Endpoints Without Authentication.

This module tests the behavior of transaction-related endpoints in scenarios
where the client is not authenticated. It ensures that the application
appropriately rejects unauthorized requests with the correct status code
and error message.

Key Features:
- **GET Transaction Endpoints**: Verifies unauthorized access to retrieve
  transaction data.
- **POST Transaction Endpoints**: Ensures unauthorized users cannot add
  transactions.
- **PATCH Transaction Endpoints**: Confirms that rollback actions require
  authentication.

Dependencies:
- `pytest`: For writing and running test cases.
- `fastapi.status`: For HTTP status code constants.
- `httpx.AsyncClient`: An asynchronous HTTP client for making requests.
- `models.enums`: Contains enumerations for transaction purposes and statuses.

Examples:
These tests simulate unauthenticated requests to the API, verifying that
all endpoints properly respond with a `401 Unauthorized` status and the
appropriate error message.
"""

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
    """
    Test unauthorized access to GET transaction endpoints.

    This test sends unauthenticated GET requests to various transaction
    endpoints and verifies that the server responds with a `401 Unauthorized`
    status and the expected error message.

    Args:
        async_client (AsyncClient): An asynchronous HTTP client for interacting
            with the FastAPI application.
        route (str): The specific route being accessed.
    """
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
    """
    Test unauthorized access to POST transaction endpoints.

    This test sends unauthenticated POST requests to the transaction endpoints
    for adding new transactions (refund or deduct) and ensures that the server
    responds with a `401 Unauthorized` status and the expected error message.

    Args:
        async_client (AsyncClient): An asynchronous HTTP client for interacting
            with the FastAPI application.
        route (str): The specific POST route being accessed.
    """
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
    async_client: AsyncClient,
) -> None:
    """
    Test unauthorized access to PATCH transaction rollback endpoint.

    This test sends an unauthenticated PATCH request to the endpoint for
    rolling back a specific transaction and ensures the server responds
    with a `401 Unauthorized` status and the expected error message.

    Args:
        async_client (AsyncClient): An asynchronous HTTP client for interacting
            with the FastAPI application.
    """
    expected_message: str = "Not authenticated"
    user_id: int = 1
    transaction_id: int = 1

    response = await async_client.patch(
        url=f"users/{user_id}/transactions/{transaction_id}",
        timeout=5,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert expected_message in response.json().values()
