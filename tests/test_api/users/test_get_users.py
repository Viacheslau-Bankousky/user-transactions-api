from typing import AsyncGenerator, Dict, List

import pytest
from fastapi import status
from httpx import AsyncClient

from core.constants import NOTHING_WAS_FOUND_MESSAGE
from models.enums import UserStatusEnum
from tests.utils.assert_checkers import check_get_user_response_assertation


@pytest.mark.asyncio
async def test_can_get_all_users(
    overridden_dependency: AsyncGenerator, async_client: AsyncClient
) -> None:
    response = await async_client.get(
        url="/users",
        timeout=5,
    )
    response_data: List[Dict] = response.json()

    assert response.status_code == status.HTTP_200_OK
    check_get_user_response_assertation(
        response_data=response_data[0],
        expected_user_id=3,
        expected_user_name="third_user",
        expected_email="third@user.com",
        expected_user_status=UserStatusEnum.BLOCKED,
    )
    check_get_user_response_assertation(
        response_data=response_data[1],
        expected_user_id=2,
        expected_user_name="second_user",
        expected_email="second@user.com",
        expected_user_status=UserStatusEnum.ACTIVE,
    )
    check_get_user_response_assertation(
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
    first_expected_user_id: int = 1
    last_expected_user_id: int = 2

    response = await async_client.get(
        url=f"/users/status/{UserStatusEnum.ACTIVE}",
        timeout=5,
    )
    response_data: List[Dict] = response.json()

    assert response.status_code == status.HTTP_200_OK
    check_get_user_response_assertation(
        response_data=response_data[0],
        expected_user_id=last_expected_user_id,
        expected_user_name="second_user",
        expected_email="second@user.com",
        expected_user_status=UserStatusEnum.ACTIVE,
    )
    check_get_user_response_assertation(
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
    expected_user_id: int = 3
    expected_user_name: str = "third_user"
    expected_email: str = "third@user.com"

    response = await async_client.get(
        url=f"/users/status/{UserStatusEnum.BLOCKED}",
        timeout=5,
    )
    response_data: List[Dict] = response.json()

    assert response.status_code == status.HTTP_200_OK
    check_get_user_response_assertation(
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
    expected_user_id: int = 1

    response = await async_client.get(
        url=route,
        timeout=5,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_200_OK
    check_get_user_response_assertation(
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
    response = await async_client.get(
        url=route,
        timeout=5,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": f"{NOTHING_WAS_FOUND_MESSAGE}",
    }
