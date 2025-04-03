"""
Module for Testing Transaction Retrieval API Endpoints.

This module contains test cases designed to validate the behavior of various
transaction retrieval endpoints under different scenarios. It ensures correct
response codes, data, and error messages based on input parameters and
conditions.

Key Features:
- **Successful Retrieval**:
  - Fetch all transactions.
  - Fetch transactions by user ID.
  - Fetch transactions by their status (e.g., PROCESSED, ROLL_BACKED).
  - Fetch transactions by user ID and status.
- **Error Validation**:
  - Invalid user IDs.
  - Invalid transaction statuses.
  - Permissions and data restrictions.

Dependencies:
- `pytest`: For defining and running test cases.
- `pytest.mark.asyncio`: For asynchronous tests.
- `fastapi.status`: For HTTP response status codes.
- `httpx.AsyncClient`: For making HTTP requests to the application.
- `core.constants.NOTHING_WAS_FOUND_MESSAGE`: Used to validate error
 scenarios.
- `models.enums`: Enumerations for transaction properties
(e.g., currency, status, purpose).
- `tests.utils.assert_checkers.assert_transaction_response`: Utility function
 to validate transaction responses.

Examples:
These test cases simulate different API requests to transaction retrieval
endpoints, both for valid and invalid inputs, to ensure proper functionality
and error handling.
"""

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
    """
    Test retrieving all transactions.

    Verifies that the API returns all transactions with correct details,
    including user IDs, amounts, purposes, and statuses.

    Args:
        overridden_dependency (AsyncGenerator): Dependency used for
                overriding or mocking behavior during the test.
        async_client (AsyncClient): Asynchronous HTTP client for
            making requests.
    """
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
    """
    Test retrieving transactions by user ID.

    Validates that transactions belonging to a specific user can be
    successfully fetched with the correct details.

    Args:
        overridden_dependency (AsyncGenerator): Dependency used for
            overriding or mocking behavior during the test.
        async_client (AsyncClient): Asynchronous HTTP client for
            making requests.
    """
    user_id: int = 1
    expected_user_id: int = 1
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
    """
    Test retrieving transactions with a nonexistent user ID.

    Verifies that the API returns an appropriate error when fetching
    transactions for a user ID that does not exist.

    Args:
        overridden_dependency (AsyncGenerator): Dependency used for
            overriding or mocking behavior during the test.
        async_client (AsyncClient): Asynchronous HTTP client for making
            requests.
    """
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
    """
    Test retrieving transactions with the status "PROCESSED".

    Verifies that transactions with the specified status can be fetched and
    contain the expected details.

    Args:
        overridden_dependency (AsyncGenerator): Dependency used for
            overriding or mocking behavior during the test.
        async_client (AsyncClient): Asynchronous HTTP client for making
            requests.
    """
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
    """
    Test retrieving transactions with the status "ROLL_BACKED".

    Validates that rollbacked transactions can be fetched and contain
    the correct details.

    Args:
        overridden_dependency (AsyncGenerator): Dependency used for
            overriding or mocking behavior during the test.
        async_client (AsyncClient): Asynchronous HTTP client for making
            requests.
    """
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
    """
    Test retrieving transactions with an invalid status.

    Ensures that an appropriate error is returned when attempting to
    query transactions with a status that does not exist.

    Args:
        overridden_dependency (AsyncGenerator): Dependency used for
            overriding or mocking behavior during the test.
        async_client (AsyncClient): Asynchronous HTTP client for making
            requests.
    """
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
    """
    Test retrieving transactions by user ID and status.

    Validates that transactions belonging to a specific user and matching
    a specific status can be fetched.

    Args:
        overridden_dependency (AsyncGenerator): Dependency used for
            overriding or mocking behavior during the test.
        async_client (AsyncClient): Asynchronous HTTP client for making
            requests.
    """
    user_id: int = 1
    expected_user_id: int = 1
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
    """
    Test retrieving transactions for a user with an invalid status.

    Ensures that the API returns an appropriate error when querying a
    user's transactions using a status that does not exist.

    Args:
        overridden_dependency (AsyncGenerator): Dependency used for
            overriding or mocking behavior during the test.
        async_client (AsyncClient): Asynchronous HTTP client for making
            requests.
    """
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
    """
    Test retrieving transactions for a nonexistent user with a valid status.

    Verifies that the API returns an appropriate error when attempting to
    query transactions for a user ID that does not exist.

    Args:
        overridden_dependency (AsyncGenerator): Dependency used for
            overriding or mocking behavior during the test.
        async_client (AsyncClient): Asynchronous HTTP client for making
            requests.
    """
    wrong_user_id: int = 1000
    transaction_status: str = TransactionStatusEnum.PROCESSED

    response = await async_client.get(
        url=f"users/{wrong_user_id}/transactions/{transaction_status}",
        timeout=5,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert NOTHING_WAS_FOUND_MESSAGE in response_data.values()
