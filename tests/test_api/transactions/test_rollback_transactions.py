"""
Module for Testing Transaction Rollback Functionality.

This module contains test cases designed to validate the rollback functionality
of transactions through API endpoints. It includes both successful rollbacks
and various scenarios where rollbacks are expected to fail.

Key Features:
- **Successful Rollbacks**:
  - Rollback refund transactions.
  - Rollback deduct transactions.
- **Error Validation**:
  - Rollbacks with invalid user IDs.
  - Rollbacks with invalid transaction IDs.
  - Rollbacks involving blocked users.

Dependencies:
- `pytest`: For defining and running test cases.
- `pytest.mark.asyncio`: For asynchronous tests.
- `fastapi.status`: For HTTP response status codes.
- `httpx.AsyncClient`: For making HTTP requests to the application.
- `core.constants.NOTHING_WAS_FOUND_MESSAGE`: To validate error scenarios.
- `models.enums`: Enumerations for transaction properties (e.g., purpose,
 status,currency).
- `tests.utils.assert_checkers.assert_transaction_response`: Utility
 function to validate transaction responses.

Examples:
These test cases simulate different API requests to rollback transactions,
covering both positive and negative scenarios, to ensure proper functionality
and error handling.
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
async def test_can_rollback_refund_transaction(
    async_client: AsyncClient,
    overridden_dependency: AsyncGenerator,
) -> None:
    """
    Test successfully rolling back a refund transaction.

    Verifies that the API correctly performs a rollback operation for
    a refund transaction and updates the transaction status to "ROLL_BACKED".

    Args:
        async_client (AsyncClient): Asynchronous HTTP client for making
            requests.
        overridden_dependency (AsyncGenerator): Dependency used for overriding
                or mocking behavior during the test.
    """
    amount = Decimal(1000)
    user_id: int = 1
    transaction_id: int = 1

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
    """
    Test successfully rolling back a deduct transaction.

    This test simulates the creation of a deduct (withdrawal) transaction,
    followed by a rollback operation to reverse its effects. It verifies
    that the rollback is performed successfully and the status is updated
    to "ROLL_BACKED".

    Args:
        overridden_dependency (AsyncGenerator): Dependency used for
            overriding or mocking behavior during the test.
        async_client (AsyncClient): Asynchronous HTTP client for
            making requests.
    """
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
    """
    Test attempting to rollback a transaction using an invalid user ID.

    Ensures that the API returns an appropriate error when a rollback is
    initiated with a nonexistent user ID.

    Args:
        overridden_dependency (AsyncGenerator): Dependency used for
            overriding or mocking behavior during the test.
        async_client (AsyncClient): Asynchronous HTTP client for making
            requests.
    """
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
    """
    Test attempting to rollback a transaction with an invalid transaction ID.

    Verifies that the API handles the error appropriately when a rollback is
    attempted with a transaction ID that does not exist.

    Args:
        overridden_dependency (AsyncGenerator): Dependency used for
            overriding or mocking behavior during the test.
        async_client (AsyncClient): Asynchronous HTTP client for making
            requests.
    """
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
    """
    Test attempting to rollback a transaction for a blocked user.

    Validates that the API restricts rollback operations for transactions
    belonging to blocked users and provides the appropriate error message.

    Args:
        overridden_dependency (AsyncGenerator): Dependency used for
            overriding or mocking behavior during the test.
        async_client (AsyncClient): Asynchronous HTTP client for making
            requests.
    """
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
