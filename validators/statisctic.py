from typing import Dict

from celery.result import AsyncResult
from fastapi import status

from core.logger_configuration import app_logger
from exceptions.validation import BadRequestDataException

MAX_WEEKS_COUNT: int = 52


def check_weeks_count(weeks_count: int) -> None:
    if weeks_count > MAX_WEEKS_COUNT:
        app_logger.info("Too many weeks")
        raise BadRequestDataException(
            message="Too many weeks", status_code=status.HTTP_400_BAD_REQUEST
        )


def check_failed_or_pending_tasks(
    task_result: AsyncResult,
) -> Dict[str, str] | None:
    for child_result in task_result.children:
        if not child_result.ready():
            app_logger.info(f"Task {child_result.id} is pending")
            return {"message": "Task is pending"}
        elif child_result.failed():
            app_logger.info(f"task ID {child_result.id} failed")
            return {"message": "Task failed"}
