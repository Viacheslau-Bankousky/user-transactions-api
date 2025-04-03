"""
Module for Testing User Retrieval API Endpoints.

This module contains test cases for validating the behavior of user retrieval
endpoints. It includes tests for fetching all users, filtering users by status,
fetching users by ID or name, and handling invalid retrieval parameters.

Key Features:
- **Retrieve All Users**:
  - Test case to fetch all users stored in the system.
- **Filter Users by Status**:
  - Validate retrieval of active and blocked users.
- **Retrieve by ID or Name**:
  - Test retrieving a user by their unique ID or name.
- **Error Handling in Retrieval**:
  - Validate behavior when invalid parameters are used (e.g., nonexistent ID,
   incorrect status).

Dependencies:
- `pytest`: For structuring and running test cases.
- `pytest.mark.asyncio`: For handling asynchronous test functions.
- `httpx.AsyncClient`: To send HTTP requests in test cases.
- `fastapi.status`: To validate HTTP status codes.
- `core.constants.NOTHING_WAS_FOUND_MESSAGE`: Used to validate not found error
 responses.
- `models.enums.UserStatusEnum`: Enumeration for user statuses (e.g., ACTIVE,
 BLOCKED).
- `tests.utils.assert_checkers.assert_get_user_response`: Utility for verifying
 user data in responses.

Examples:
The test cases simulate various scenarios to ensure the API accurately
supports retrieving user information based on ID, name, or status, while
correctly handling invalid input.
"""

from typing import AsyncGenerator, Dict, List

import pytest
from fastapi import status
from httpx import AsyncClient

from core.constants import NOTHING_WAS_FOUND_MESSAGE
from models.enums import UserStatusEnum
from tests.utils.assert_checkers import assert_get_user_response


@pytest.mark.asyncio
async def test_can_get_all_users(
    overridden_dependency: AsyncGenerator, async_client: AsyncClient
) -> None:
    """
    Test retrieving all users.

    Verifies that the API can retrieve all users, returning them in the
    expected order along with accurate attributes such as name, email,
    and status.

    Args:
        overridden_dependency (AsyncGenerator): Dependency injection for
            mocking services.
        async_client (AsyncClient): Asynchronous HTTP client for sending
            requests.
    """
    response = await async_client.get(
        url="/users",
        timeout=5,
    )
    response_data: List[Dict] = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert_get_user_response(
        response_data=response_data[0],
        expected_user_id=3,
        expected_user_name="third_user",
        expected_email="third@user.com",
        expected_user_status=UserStatusEnum.BLOCKED,
    )
    assert_get_user_response(
        response_data=response_data[1],
        expected_user_id=2,
        expected_user_name="second_user",
        expected_email="second@user.com",
        expected_user_status=UserStatusEnum.ACTIVE,
    )
    assert_get_user_response(
        response_data=response_data[2],
        expected_user_id=1,
        expected_user_name="first_user",
        expected_email="first@user.com",
        expected_user_status=UserStatusEnum.ACTIVE,
    )


@pytest.mark.asyncio
async def test_can_get_active_users(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    """
    Test retrieving all active users.

    Verifies that the API can filter users by their status, specifically
    fetching users with the "ACTIVE" status.

    Args:
        overridden_dependency (AsyncGenerator): Dependency injection for
            mocking services.
        async_client (AsyncClient): Asynchronous HTTP client for sending
            requests.
    """
    first_expected_user_id: int = 1
    last_expected_user_id: int = 2

    response = await async_client.get(
        url=f"/users/status/{UserStatusEnum.ACTIVE}",
        timeout=5,
    )
    response_data: List[Dict] = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert_get_user_response(
        response_data=response_data[0],
        expected_user_id=last_expected_user_id,
        expected_user_name="second_user",
        expected_email="second@user.com",
        expected_user_status=UserStatusEnum.ACTIVE,
    )
    assert_get_user_response(
        response_data=response_data[1],
        expected_user_id=first_expected_user_id,
        expected_user_name="first_user",
        expected_email="first@user.com",
        expected_user_status=UserStatusEnum.ACTIVE,
    )


@pytest.mark.asyncio
async def test_can_get_users_with_blocked_status(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    """
    Test retrieving users with a "BLOCKED" status.

    Verifies that the API can filter users by their status, fetching
    only users whose status is "BLOCKED."

    Args:
        overridden_dependency (AsyncGenerator): Dependency injection
            for mocking services.
        async_client (AsyncClient): Asynchronous HTTP client for sending
            requests.
    """
    expected_user_id: int = 3
    expected_user_name: str = "third_user"
    expected_email: str = "third@user.com"

    response = await async_client.get(
        url=f"/users/status/{UserStatusEnum.BLOCKED}",
        timeout=5,
    )
    response_data: List[Dict] = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert_get_user_response(
        response_data=response_data[0],
        expected_user_id=expected_user_id,
        expected_user_name=expected_user_name,
        expected_email=expected_email,
        expected_user_status=UserStatusEnum.BLOCKED,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("route", ["/users/1", "/users/first_user"])
async def test_can_get_user_by_id_and_name(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
    route: str,
) -> None:
    """
    Test retrieving a user by ID or name.

    Validates that the API correctly retrieves user data based on either
    the user's unique ID or their name.

    Args:
        overridden_dependency (AsyncGenerator): Dependency injection for
            mocking services.
        async_client (AsyncClient): Asynchronous HTTP client for sending
            requests.
        route (str): API route used for retrieval (e.g., by ID or name).
    """
    expected_user_id: int = 1

    response = await async_client.get(
        url=route,
        timeout=5,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert_get_user_response(
        response_data=response_data,
        expected_user_id=expected_user_id,
        expected_user_name="first_user",
        expected_email="first@user.com",
        expected_user_status=UserStatusEnum.ACTIVE,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route",
    [
        "/users/1000",
        "/users/status/INCORRECT_STATUS",
        "/users/incorrect_name",
    ],
)
async def test_can_not_get_user_by_invalid_params(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
    route: str,
) -> None:
    """
    Test handling invalid parameters in user retrieval.

    Verifies that the API returns a 404 error when an invalid user ID,
    status, or name is provided, demonstrating proper error handling.

    Args:
        overridden_dependency (AsyncGenerator): Dependency injection
            for mocking services.
        async_client (AsyncClient): Asynchronous HTTP client for
            sending requests.
        route (str): API route used with invalid parameters.
    """
    response = await async_client.get(
        url=route,
        timeout=5,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": f"{NOTHING_WAS_FOUND_MESSAGE}",
    }
