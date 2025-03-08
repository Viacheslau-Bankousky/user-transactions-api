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
