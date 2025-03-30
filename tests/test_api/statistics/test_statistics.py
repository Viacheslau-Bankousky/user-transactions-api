from typing import AsyncGenerator, Dict

import pytest
from fastapi import status
from httpx import AsyncClient

# from tests.utils.assert_checkers import check_statistics_response_assertation


@pytest.mark.asyncio
async def test_can_start_statistics_analise(
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
@pytest.mark.parametrize(
    "route, expected_message",
    [
        ("/transactions/analysis/period/100", "Too many weeks"),
        ("/transactions/analysis/period/0", "Low number of weeks"),
    ],
)
async def test_can_not_start_statistics_analise_with_wrong_weeks_count(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
    route: str,
    expected_message: str,
) -> None:
    response = await async_client.get(
        url=route,
        timeout=5,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response_data["detail"] == expected_message


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route",
    ["/transactions/analysis/period/1", "/transactions/analysis/status/1"],
)
async def test_can_not_get_statistics_without_authentication(
    async_client: AsyncClient,
    route: str,
) -> None:
    expected_message: str = "Not authenticated"

    response = await async_client.get(
        url=route,
        timeout=5,
    )
    response_data: Dict = response.json().values()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert expected_message in response_data


# @pytest.mark.asyncio
# async def test_can_get_pending_statistics_result(
#     overridden_dependency: AsyncGenerator,
#     async_client: AsyncClient,
# ) -> None:
#     weeks_count: int = 8
#     expected_message: str = "Task is pending"
#
#     task_response = await async_client.get(
#         url=f"/transactions/analysis/period/{weeks_count}",
#         timeout=5,
#     )
#     task_response_data: Dict = task_response.json()
#     task_id: str = task_response_data["task_id"]
#     statistics_response = await async_client.get(
#         url=f"/transactions/analysis/status/{task_id}",
#         timeout=5,
#     )
#     statistics_response_data: Dict = statistics_response.json()
#     assert statistics_response.status_code == status.HTTP_200_OK
#     assert statistics_response_data["message"] == expected_message
