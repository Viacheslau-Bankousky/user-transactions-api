from typing import AsyncGenerator, Dict

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_can_get_statistics(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    weeks_count: int = 1

    response = await async_client.get(
        url=f"/transactions/analysis/period/{weeks_count}",
        timeout=5,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert "task_id" in response_data
    assert isinstance(response_data["task_id"], str)


@pytest.mark.asyncio
async def test_can_not_get_statistics_with_too_much_weeks_count(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    weeks_count: int = 100
    expected_message: str = "Too many weeks"

    response = await async_client.get(
        url=f"/transactions/analysis/period/{weeks_count}",
        timeout=5,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response_data["detail"] == expected_message


@pytest.mark.asyncio
async def test_can_not_get_statistics_without_authentication(
    async_client: AsyncClient,
) -> None:
    weeks_count: int = 1
    expected_message: str = "Not authenticated"

    response = await async_client.get(
        url=f"/transactions/analysis/period/{weeks_count}",
        timeout=5,
    )
    response_data: Dict = response.json().values()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert expected_message in response_data
