from typing import Dict

import pytest
from fastapi import status
from httpx import AsyncClient

from authentication.user_management import check_user_has_token


@pytest.mark.asyncio
async def test_login_for_access_token_async(async_client: AsyncClient):
    form_data: Dict[str, str] = {
        "username": "fourth_user",
        "password": "<PASSWORD4>",
    }

    response = await async_client.post(url="/token", timeout=5, data=form_data)
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_user_has_token(async_client: AsyncClient):
    form_data: Dict[str, str] = {
        "username": "fourth_user",
        "password": "<PASSWORD4>",
    }

    response = await async_client.post(url="/token", timeout=5, data=form_data)
    response_data = response.json()

    assert check_user_has_token(response_data["access_token"])
