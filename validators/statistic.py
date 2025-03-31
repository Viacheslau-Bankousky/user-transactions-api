"""
Module for validating input data and monitoring Celery task statuses.

This module provides utility functions for validating weeks-related
input and monitoring the status of Celery tasks, specifically
checking if tasks are pending or have failed.
It also includes logging for better traceability and feedback for
invalid inputs or task issues.

Key Features:
- **Input Validation**: Validates the number of weeks provided by
 the user to ensure it does not exceed a predefined limit.
- **Task Monitoring**: Checks the status of Celery tasks
 (e.g., pending or failed).
- **Logging**: Provides detailed logs for all validation and
 monitoring steps.

Dependencies:
- Celery's `AsyncResult` is used for task result monitoring.
- FastAPI's `status` for HTTP status codes in exception handling.
- A custom `BadRequestDataException` is used for validation errors.
- Logging is handled through the application’s central logger
 (`app_logger`).

Constants:
- **MAX_WEEKS_COUNT**: Defines the maximum allowed weeks (currently 52).

Functions:
- **check_weeks_count**: Validates that a given number of weeks does not
  exceed the maximum allowed limit.
- **check_failed_or_pending_tasks**: Inspects the status of Celery task
 results to identify if any task is either pending or failed.
"""

from typing import Dict

from celery.result import AsyncResult
from fastapi import status

from core.logger_configuration import app_logger
from exceptions.validation import BadRequestDataException

MAX_WEEKS_COUNT: int = 52


def check_weeks_count(weeks_count: int) -> None:
    """
    Validate the specified number of weeks.

    This function checks if the provided `weeks_count` exceeds the maximum
    allowed limit (`MAX_WEEKS_COUNT`) or is less than 1.
    If it does, an exception is raised, and the action is logged.

    Args:
        weeks_count (int): The number of weeks to validate.

    Raises:
        BadRequestDataException: If `weeks_count` is greater than
            `MAX_WEEKS_COUNT` or less than 1.
    """
    if weeks_count > MAX_WEEKS_COUNT:
        app_logger.info("Too many weeks")
        raise BadRequestDataException(
            message="Too many weeks", status_code=status.HTTP_400_BAD_REQUEST
        )
    elif weeks_count < 1:
        raise BadRequestDataException(
            message="Low number of weeks",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


def check_failed_or_pending_tasks(
    task_result: AsyncResult,
) -> Dict[str, str] | None:
    """
    Check the status of Celery tasks to identify pending or failed results.

    This function iterates through the children of a specified `AsyncResult`
    object and checks whether each task is either pending or has failed.
    If such a task is found, a dictionary with an appropriate message is
    returned. All findings are logged for traceability.

    Args:
        task_result (AsyncResult): The Celery task result object to inspect.

    Returns:
        Dict[str, str] | None: A dictionary containing a message if a task
            is pending or failed, otherwise `None`.
    """
    for child_result in task_result.children:
        if not child_result.ready():
            app_logger.info(f"Task {child_result.id} is pending")
            return {"message": "Task is pending"}
        elif child_result.failed():
            app_logger.info(f"task ID {child_result.id} failed")
            return {"message": "Task failed"}
