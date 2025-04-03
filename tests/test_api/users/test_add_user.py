"""
Module for Testing User Creation API Endpoints.

This module contains test cases designed to validate the behavior of the user
creation API. It covers successful user creation, as well as validation and
conflict scenarios during the user registration process.

Key Features:
- **Successful User Creation**:
  - Test the creation of a new user with valid parameters.
- **Validation Errors**:
  - Ensure the inability to create users without required fields.
- **Conflict Errors**:
  - Validate that the API prevents the creation of duplicate users.

Dependencies:
- `pytest`: For defining test cases.
- `pytest.mark.asyncio`: For asynchronous test execution.
- `fastapi.status`: For HTTP response status codes.
- `httpx.AsyncClient`: For making HTTP requests to the API.
- `models.enums.UserStatusEnum`: Represents user status (e.g., ACTIVE).
- `tests.utils.assert_checkers.assert_user_change_response`: Utility function
 to validate user creation responses.

Examples:
The test cases simulate user creation scenarios, ensuring correctness for
varying inputs and edge cases.
"""

from typing import Any, AsyncGenerator, Dict

import pytest
from fastapi import status
from httpx import AsyncClient

from models.enums import UserStatusEnum
from tests.utils.assert_checkers import (
    assert_user_change_response,
)


@pytest.mark.asyncio
async def test_can_add_user(async_client: AsyncClient) -> None:
    """
    Test successful user creation.

    Validates that a user can be successfully created with valid
    input parameters and verifies the attributes of the created user.

    Args:
        async_client (AsyncClient): Asynchronous HTTP client for making
            API requests.
    """
    new_user_data: Dict[str, str] = {
        "name": "new_user",
        "email": "new@user.com",
        "password": "new_password",
    }
    expected_user_id: int = 4

    response = await async_client.post(
        url="/users",
        timeout=5,
        json=new_user_data,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert_user_change_response(
        response_data=response_data,
        expected_user_id=expected_user_id,
        expected_user_name="new_user",
        expected_email="new@user.com",
        expected_user_status=UserStatusEnum.ACTIVE,
    )


@pytest.mark.asyncio
async def test_can_not_add_user_without_required_params(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    """
    Test failure to create a user without mandatory fields.

    Verifies that the API returns validation errors when required fields
    (e.g., name, password) are omitted in the user creation request.

    Args:
        overridden_dependency (AsyncGenerator): Dependency injection for
            mocking services.
        async_client (AsyncClient): Asynchronous HTTP client for making
            API requests.
    """
    not_enough_params_to_add_user: Dict[str, str] = {"email": "new@user.com"}

    response = await async_client.post(
        url="/users",
        timeout=5,
        json=not_enough_params_to_add_user,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response_data["detail"][0]["msg"] == "Field required"


@pytest.mark.asyncio
async def test_can_not_add_the_same_user_twice(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    """
    Test preventing the creation of duplicate users.

    Validates that the system does not allow adding a user with the same
    email more than once, returning a conflict error.

    Args:
        overridden_dependency (AsyncGenerator): Dependency injection for
            mocking services.
        async_client (AsyncClient): Asynchronous HTTP client for making
            API requests.
    """
    new_user_data: Dict[str, str] = {
        "name": "new_user",
        "email": "new@user.com",
        "password": "new_password",
    }

    await async_client.post(
        url="/users",
        timeout=5,
        json=new_user_data,
    )
    response = await async_client.post(
        url="/users",
        timeout=5,
        json=new_user_data,
    )
    response_data: Dict[str, Any] = response.json()

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response_data["detail"] == "User already exists"
