from typing import Any, Dict

import pytest
from fastapi import status
from httpx import AsyncClient

from models.enums import UserStatusEnum
from tests.utils.assert_checkers import (
    check_user_change_response,
)


@pytest.mark.asyncio
async def test_can_add_user(async_client: AsyncClient) -> None:
    new_user_data: Dict[str, str] = {
        "name": "new_user",
        "email": "new@user.com",
    }

    response = await async_client.post(
        url="/users",
        timeout=5,
        json=new_user_data,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    check_user_change_response(
        response_data=response_data,
        expected_user_id=3,
        expected_user_name="new_user",
        expected_email="new@user.com",
        expected_user_status=UserStatusEnum.ACTIVE,
    )


@pytest.mark.asyncio
async def test_can_not_add_user_without_required_params(
        async_client: AsyncClient,
) -> None:
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
        async_client: AsyncClient,
) -> None:
    new_user_data: Dict[str, str] = {
        "name": "new_user",
        "email": "new@user.com",
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
