from typing import Dict, List

import pytest
from fastapi import status
from httpx import AsyncClient

from core.constants import NOTHING_WAS_FOUND_MESSAGE
from tests.utils.assert_checkers import check_get_user_response_assertation

from models.enums import UserStatusEnum


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route", ["/users", f"/users/status/{UserStatusEnum.ACTIVE}"]
)
async def test_can_get_users_include_active(
        async_client: AsyncClient, route: str
) -> None:
    response = await async_client.get(
        url=route,
        timeout=5,
    )
    response_data: List[Dict] = response.json()

    assert response.status_code == status.HTTP_200_OK
    check_get_user_response_assertation(
        response_data=response_data[0],
        expected_user_id=2,
        expected_user_name="last_user",
        expected_email="last@user.com",
    )
    check_get_user_response_assertation(
        response_data=response_data[1],
        expected_user_id=1,
        expected_user_name="first_user",
        expected_email="first@user.com",
    )


@pytest.mark.asyncio
async def test_can_get_users_with_blocked_status(
        async_client: AsyncClient,
) -> None:
    response = await async_client.get(
        url=f"/users/status/{UserStatusEnum.BLOCKED}",
        timeout=5,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.asyncio
@pytest.mark.parametrize("route", ["/users/1", "/users/first_user"])
async def test_can_get_user_by_id_and_name(
        async_client: AsyncClient, route: str
) -> None:
    response = await async_client.get(
        url=route,
        timeout=5,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_200_OK
    check_get_user_response_assertation(
        response_data=response_data,
        expected_user_id=1,
        expected_user_name="first_user",
        expected_email="first@user.com",
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
        async_client: AsyncClient, route: str
) -> None:
    response = await async_client.get(
        url=route,
        timeout=5,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": f"{NOTHING_WAS_FOUND_MESSAGE}",
    }
