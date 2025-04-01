from typing import AsyncGenerator, Dict, List

import pytest
from fastapi import status
from httpx import AsyncClient
from unittest.mock import patch, MagicMock

from tests.utils.assert_checkers import assert_statistics_response


@patch("statistic.tasks.processing.calculate_statistics_for_all_dates.s")
@pytest.mark.asyncio
async def test_start_statistics_analise(
    mocked_celery_task,
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    task_id: str = "mocked_task_id"
    mock_async_result = MagicMock()
    mock_async_result.id = task_id
    mocked_celery_task.return_value.apply_async.return_value = (
        mock_async_result
    )

    response = await async_client.get(
        url="/transactions/analysis/period/1",
        timeout=5,
    )
    response_data: Dict = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert "task_id" in response_data
    assert response_data["task_id"] == task_id
    mocked_celery_task.return_value.apply_async.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route, expected_message",
    [
        ("/transactions/analysis/period/100", "Too many weeks"),
        ("/transactions/analysis/period/0", "Low number of weeks"),
    ],
)
async def test_statistics_analise_with_wrong_weeks_count_error(
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
async def test_get_statistics_without_authentication_error(
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


@patch("routes.transactions.check_failed_or_pending_tasks")
@pytest.mark.asyncio
async def test_get_pending_statistics_result(
    mocked_task_checker,
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    expected_message: str = "Task is pending"
    pending_task_id: str = "pending_task_id"
    mocked_task_checker.return_value = {"message": expected_message}

    statistics_response = await async_client.get(
        url=f"/transactions/analysis/status/{pending_task_id}",
        timeout=5,
    )
    statistics_response_data: Dict = statistics_response.json()

    assert statistics_response.status_code == status.HTTP_200_OK
    assert statistics_response_data["message"] == expected_message


@patch("routes.transactions.AsyncResult")
@patch("routes.transactions.check_failed_or_pending_tasks")
@patch("statistic.tasks.processing.calculate_statistics_for_all_dates.s")
@pytest.mark.asyncio
async def test_can_get_statistics_result(
    mocked_celery_task,
    mocked_task_checker,
    mocked_async_result,
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    mock_async_result = MagicMock()
    statistics_response: Dict = {
        "start_date": "2023-01-01",
        "end_date": "2023-01-31",
        "registered_users_count": 0,
        "registered_and_deposit_users_count": 0,
        "registered_and_not_rollbacked_deposit_users_count": 0,
        "not_rollbacked_deposit_amount": 0,
        "not_rollbacked_withdraw_amount": 0,
        "transactions_count": 0,
        "not_rollbacked_transactions_count": 0,
    }
    mock_async_result.id = "mocked_task_id"
    mocked_celery_task.return_value.apply_async.return_value = (
        mock_async_result
    )
    mocked_task_checker.return_value = None
    mocked_async_result.get.return_value = statistics_response

    response = await async_client.get(
        url="/transactions/analysis/period/1",
        timeout=5,
    )
    response_data: Dict = response.json()
    task_id: str = response_data["task_id"]
    response = await async_client.get(
        url=f"/transactions/analysis/status/{task_id}",
        timeout=5,
    )
    response_data: List[Dict] = response.json()

    for item in response_data:
        assert_statistics_response(
            response_data=item,
            start_date="2023-01-01",
            end_date="2023-01-31",
            registered_users_count=0,
            registered_and_deposit_users_count=0,
            registered_and_not_rollbacked_deposit_users_count=0,
            not_rollbacked_deposit_amount=0,
            not_rollbacked_withdraw_amount=0,
            transactions_count=0,
            not_rollbacked_transactions_count=0,
        )
