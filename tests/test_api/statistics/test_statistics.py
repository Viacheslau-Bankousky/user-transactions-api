"""
Module for Testing Transaction Statistics Analysis.

This module contains test cases for verifying the transaction analysis
functionality, which includes starting statistics calculation tasks,
retrieving task results, handling authentication, and validating input
errors for incorrect parameters.

Key Features:
- **Start Statistics Calculation**:
  - Test initiating Celery tasks for computing transaction statistics.
- **Handle Input Validation Errors**:
  - Verify behavior when invalid periods or incorrect weeks count are
   provided.
- **Authentication Handling**:
  - Ensure unauthorized requests return the appropriate error response.
- **Retrieve Task Results**:
  - Mock task execution and validate the retrieved statistics using
   the task ID.
- **Pending Task Handling**:
  - Test the pending task state and appropriate API responses.

Dependencies:
- `pytest`: For test structuring and execution.
- `pytest.mark.asyncio`: For handling asynchronous test functions.
- `unittest.mock.patch`: To mock Celery tasks and task results in
 tests.
- `httpx.AsyncClient`: For making HTTP requests in test cases.
- `tests.utils.assert_checkers.assert_statistics_response`: Utility
to validate the statistics data in task results.

Examples:
The test cases simulate the process of initiating transaction
statistics calculations, handling task states, and handling errors
effectively, ensuring robust API behavior.
"""

from typing import AsyncGenerator, Dict, List

import pytest
from fastapi import status
from httpx import AsyncClient
from unittest.mock import patch, MagicMock

from tests.utils.assert_checkers import assert_statistics_response


@patch("statistic.tasks.processing.calculate_statistics_for_all_dates.s")
@pytest.mark.asyncio
async def test_start_statistics_analysis(
    mocked_celery_task,
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    """
    Test starting transaction statistics calculation.

    Verifies that the API successfully starts a statistics calculation task in
    Celery and returns the appropriate `task_id` in the response.

    Mocks:
        - Celery task initiation.

    Args:
        mocked_celery_task: Mocked Celery task to simulate task initiation.
        overridden_dependency (AsyncGenerator): Dependency injection for
            mocking services.
        async_client (AsyncClient): Asynchronous HTTP client for sending
            requests.
    """
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
async def test_statistics_analysis_with_wrong_weeks_count_error(
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
    route: str,
    expected_message: str,
) -> None:
    """
    Test error handling for invalid weeks count in statistics analysis.

    Validates that the API returns appropriate error messages when the
    weeks count is too low or exceeds acceptable limits.

    Args:
        overridden_dependency (AsyncGenerator): Dependency injection for
            mocking services.
        async_client (AsyncClient): Asynchronous HTTP client for sending
            requests.
        route (str): The API route.
        expected_message (str): Expected error message in the response.
    """
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
    """
    Test error response for unauthenticated requests.

    Verifies that the API returns a `401 UNAUTHORIZED` status for requests
    made without authentication credentials.

    Args:
        async_client (AsyncClient): Asynchronous HTTP client for sending
            requests.
        route (str): The API route to test.
    """
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
    """
    Test retrieving pending transaction statistics task result.

    Verifies that the API correctly handles pending task states by returning
    an appropriate message indicating that the task is still pending.

    Mocks:
        - Task state retrieval to simulate a pending task.

    Args:
        mocked_task_checker: Mocked task checker to simulate pending tasks.
        overridden_dependency (AsyncGenerator): Dependency injection for
            mocking services.
        async_client (AsyncClient): Asynchronous HTTP client for sending
            requests.
    """
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
@patch("statistic.tasks.processing.calculate_statistics_for_all_dates.s")
@pytest.mark.asyncio
async def test_can_get_statistics_result(
    mocked_celery_task,
    mocked_async_result,
    overridden_dependency: AsyncGenerator,
    async_client: AsyncClient,
) -> None:
    """
    Test retrieving final statistics result.

    Verifies the API's ability to retrieve completed statistics calculation
    task results. The results are validated against expected statistics data.

    Mocks:
        - Celery task result retrieval.
        - Statistics calculation task initiation.

    Args:
        mocked_celery_task: Mocked Celery task to simulate task initiation.
        mocked_async_result: Mocked Celery task result to simulate completed
            results.
        overridden_dependency (AsyncGenerator): Dependency injection for
            mocking services.
        async_client (AsyncClient): Asynchronous HTTP client for sending
            requests.
    """
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

    for statistics_item in response_data:
        assert_statistics_response(
            response_data=statistics_item,
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
