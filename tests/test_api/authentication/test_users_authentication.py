"""
Module for Testing User Endpoints Without Authentication.

This module tests the behavior of API endpoints related to user management in
cases where the client is not authenticated. It ensures that the application
responds appropriately to unauthorized requests with the correct HTTP status
code and error message.

Key Features:
- **GET User Endpoints**: Verifies unauthorized access for retrieving user
 data, including filtered and specific user lookups.
- **PATCH User Endpoints**: Ensures unauthenticated clients cannot modify user
  information.

Dependencies:
- `pytest`: For writing and running test cases.
- `fastapi.status`: For HTTP status code constants.
- `httpx.AsyncClient`: An asynchronous HTTP client for making requests.
- `models.enums.UserStatusEnum`: Enumeration representing user status states
  like `ACTIVE` or `BLOCKED`.

Examples:
These tests simulate unauthenticated API requests to user-related endpoints and
verify that `401 Unauthorized` responses are returned along with the expected
error message.
"""

from typing import Dict

import pytest
from fastapi import status
from httpx import AsyncClient

from models.enums import UserStatusEnum


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route",
    [
        "/users",
        f"/users/status/{UserStatusEnum.ACTIVE}",
        f"/users/status/{UserStatusEnum.BLOCKED}",
        "/users/1",
        "/users/first_user",
    ],
)
async def test_can_not_get_users_without_authentication(
    async_client: AsyncClient, route: str
) -> None:
    """
    Test unauthorized access to GET user endpoints.

    This test sends unauthenticated GET requests to various user-related
    endpoints and verifies that the server responds with `401 Unauthorized`
    and the appropriate error message.

    Args:
        async_client (AsyncClient): An asynchronous HTTP client for interacting
            with the FastAPI application.
        route (str): The specific GET route being accessed.
    """
    expected_message: str = "Not authenticated"

    response = await async_client.get(
        url=route,
        timeout=5,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert expected_message in response.json().values()


@pytest.mark.asyncio
async def test_can_not_change_users_without_authentication(
    async_client: AsyncClient,
) -> None:
    """
    Test unauthorized access to PATCH user endpoints.

    This test sends an unauthenticated PATCH request to update user
    information, including name, email, and status, and verifies that
    the server responds with `401 Unauthorized` and the appropriate
    error message.

    Args:
        async_client (AsyncClient): An asynchronous HTTP client for interacting
            with the FastAPI application.
    """
    all_changing_params_for_user: Dict[str, str] = {
        "name": "updated_user",
        "email": "updated@user.com",
        "status": UserStatusEnum.BLOCKED,
    }
    expected_message: str = "Not authenticated"

    response = await async_client.patch(
        url="/users/2",
        timeout=5,
        json=all_changing_params_for_user,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert expected_message in response.json().values()
