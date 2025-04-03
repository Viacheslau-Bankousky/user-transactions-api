"""
Module for Testing User Update API Endpoints.

This module contains test cases designed to validate the behavior of the user
update API, including scenarios where changes are successful and cases where
errors occur due to invalid inputs or nonexistent users.

Key Features:
- **Successful User Updates**:
  - Update all user details (name, email, status).
  - Update individual user details (name, email, and status).
- **Failure Scenarios**:
  - Validate error when attempting to update a nonexistent user.
  - Ensure validation errors for invalid status values.

Dependencies:
- `pytest`: For defining the test cases.
- `pytest.mark.asyncio`: For handling asynchronous test functions.
- `fastapi.status`: For using standard HTTP status codes for validation.
- `httpx.AsyncClient`: For sending HTTP requests in tests.
- `core.constants.NOTHING_WAS_FOUND_MESSAGE`: Used to validate error responses.
- `models.enums.UserStatusEnum`: Enum for user statuses
 (e.g., ACTIVE, BLOCKED).
- `tests.utils.assert_checkers.assert_user_change_response`: Utility function
 for validating user update responses.

Examples:
The test cases simulate update, validation, and error scenarios for API
behavior related to user updates.
"""

from typing import Any, AsyncGenerator, Dict, List

import pytest
from fastapi import status
from httpx import AsyncClient

from core.constants import NOTHING_WAS_FOUND_MESSAGE
from models.enums import UserStatusEnum
from tests.utils.assert_checkers import (
    assert_user_change_response,
)


@pytest.mark.asyncio
async def test_can_change_all_user_data(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    """
    Test updating all user details (name, email, and status).

    Verifies that the API allows updating multiple attributes of a user in
    a single request.

    Args:
        overridden_dependency (AsyncGenerator): Dependency injection for
            mocking services.
        async_client (AsyncClient): Asynchronous HTTP client for making API
            requests.
    """
    all_changing_params_for_user: Dict[str, str] = {
        "name": "updated_user",
        "email": "updated@user.com",
        "status": UserStatusEnum.BLOCKED,
    }

    response = await async_client.patch(
        url="/users/2",
        timeout=5,
        json=all_changing_params_for_user,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert_user_change_response(
        response_data=response_data,
        expected_user_id=2,
        expected_user_name="updated_user",
        expected_email="updated@user.com",
        expected_user_status=UserStatusEnum.BLOCKED,
    )


@pytest.mark.asyncio
async def test_can_change_user_name(
    overridden_dependency: AsyncGenerator, async_client: AsyncClient
) -> None:
    """
    Test updating a user's name.

    Verifies that the API allows modifying a user's name while keeping other
    details unchanged.

    Args:
        overridden_dependency (AsyncGenerator): Dependency injection for
            mocking services.
        async_client (AsyncClient): Asynchronous HTTP client for making
            API requests.
    """
    user_name_changing_params: Dict[str, str] = {"name": "updated_user"}

    response = await async_client.patch(
        url="/users/2",
        timeout=5,
        json=user_name_changing_params,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert_user_change_response(
        response_data=response_data,
        expected_user_id=2,
        expected_user_name="updated_user",
        expected_email="second@user.com",
        expected_user_status=UserStatusEnum.ACTIVE,
    )


@pytest.mark.asyncio
async def test_can_change_user_email(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    """
    Test updating a user's email.

    Verifies that the API allows modifying a user's email while keeping
    other details unchanged.

    Args:
        overridden_dependency (AsyncGenerator): Dependency injection for
            mocking services.
        async_client (AsyncClient): Asynchronous HTTP client for making
            API requests.
    """
    user_email_changing_params: Dict[str, str] = {"email": "updated@user.com"}

    response = await async_client.patch(
        url="/users/2",
        timeout=5,
        json=user_email_changing_params,
    )
    response_data: Dict[str, Any] = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert_user_change_response(
        response_data=response_data,
        expected_user_id=2,
        expected_user_name="second_user",
        expected_email="updated@user.com",
        expected_user_status=UserStatusEnum.ACTIVE,
    )


@pytest.mark.asyncio
async def test_can_change_user_status(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    """
    Test updating a user's status.

    Verifies that the API allows modifying a user's status (e.g., ACTIVE to
    BLOCKED) while retaining other details unchanged.

    Args:
        overridden_dependency (AsyncGenerator): Dependency injection for
            mocking services.
        async_client (AsyncClient): Asynchronous HTTP client for making
            API requests.
    """
    user_status_changing_params: Dict[str, str] = {"status": "BLOCKED"}

    response = await async_client.patch(
        url="/users/2",
        timeout=5,
        json=user_status_changing_params,
    )
    response_data: Dict[str, Any] = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert_user_change_response(
        response_data=response_data,
        expected_user_id=2,
        expected_user_name="second_user",
        expected_email="second@user.com",
        expected_user_status=UserStatusEnum.BLOCKED,
    )


@pytest.mark.asyncio
async def test_can_not_change_nonexistent_user(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    """
    Test attempting to update a nonexistent user.

    Verifies that the API returns an appropriate error response when attempting
    to update a user that does not exist.

    Args:
        overridden_dependency (AsyncGenerator): Dependency injection for
            mocking services.
        async_client (AsyncClient): Asynchronous HTTP client for making
            API requests.
    """
    all_changing_params_for_user: Dict[str, str] = {
        "name": "updated_user",
        "email": "updated@user.com",
        "status": UserStatusEnum.BLOCKED,
    }

    response = await async_client.patch(
        url="/users/1000",
        timeout=5,
        json=all_changing_params_for_user,
    )
    response_data: Dict[str, Any] = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_data["detail"] == NOTHING_WAS_FOUND_MESSAGE


@pytest.mark.asyncio
async def test_can_not_change_user_using_invalid_status(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    """
    Test updating a user's status using an invalid or unsupported status value.

    Ensures that the API returns validation errors when an invalid status value
    is provided in the request.

    Args:
        overridden_dependency (AsyncGenerator): Dependency injection for
            mocking services.
        async_client (AsyncClient): Asynchronous HTTP client for making API
            requests.
    """
    incorrect_changing_params_for_user: Dict[str, str] = {
        "status": "incorrect_status"
    }

    response = await async_client.patch(
        url="/users/2",
        timeout=5,
        json=incorrect_changing_params_for_user,
    )
    response_data: List[Dict[str, Any]] = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        "Input should be" in response_data["detail"][0]["msg"]  # type: ignore
    )
