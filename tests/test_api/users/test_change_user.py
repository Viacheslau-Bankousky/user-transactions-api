from typing import Any, Dict, List

import pytest
from fastapi import status
from httpx import AsyncClient

from core.constants import NOTHING_WAS_FOUND_MESSAGE
from models.enums import UserStatusEnum
from tests.utils.assert_checkers import (
    check_user_change_response,
)


@pytest.mark.asyncio
async def test_can_change_all_user_data(
        async_client: AsyncClient,
) -> None:
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
    check_user_change_response(
        response_data=response_data,
        expected_user_id=2,
        expected_user_name="updated_user",
        expected_email="updated@user.com",
        expected_user_status=UserStatusEnum.BLOCKED,
    )


@pytest.mark.asyncio
async def test_can_change_user_name(async_client: AsyncClient) -> None:
    user_name_changing_params: Dict[str, str] = {"name": "updated_user"}

    response = await async_client.patch(
        url="/users/2",
        timeout=5,
        json=user_name_changing_params,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_200_OK
    check_user_change_response(
        response_data=response_data,
        expected_user_id=2,
        expected_user_name="updated_user",
        expected_email="last@user.com",
        expected_user_status=UserStatusEnum.ACTIVE,
    )


@pytest.mark.asyncio
async def test_can_change_user_email(
        async_client: AsyncClient,
) -> None:
    user_email_changing_params: Dict[str, str] = {"email": "updated@user.com"}

    response = await async_client.patch(
        url="/users/2",
        timeout=5,
        json=user_email_changing_params,
    )
    response_data: Dict[str, Any] = response.json()

    assert response.status_code == status.HTTP_200_OK
    check_user_change_response(
        response_data=response_data,
        expected_user_id=2,
        expected_user_name="last_user",
        expected_email="updated@user.com",
        expected_user_status=UserStatusEnum.ACTIVE,
    )


@pytest.mark.asyncio
async def test_can_change_user_status(
        async_client: AsyncClient,
) -> None:
    user_status_changing_params: Dict[str, str] = {"status": "BLOCKED"}

    response = await async_client.patch(
        url="/users/2",
        timeout=5,
        json=user_status_changing_params,
    )
    response_data: Dict[str, Any] = response.json()

    assert response.status_code == status.HTTP_200_OK
    check_user_change_response(
        response_data=response_data,
        expected_user_id=2,
        expected_user_name="last_user",
        expected_email="last@user.com",
        expected_user_status=UserStatusEnum.BLOCKED,
    )


@pytest.mark.asyncio
async def test_can_not_change_nonexistent_user(
        async_client: AsyncClient,
) -> None:
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
        async_client: AsyncClient,
) -> None:
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
