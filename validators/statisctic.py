from celery.result import AsyncResult
from fastapi import status

from core.logger_configuration import app_logger
from exceptions.celery import CeleryException
from exceptions.validation import BadRequestDataException

MAX_WEEKS_COUNT: int = 52


def check_weeks_count(weeks_count: int) -> None:
    if weeks_count > MAX_WEEKS_COUNT:
        app_logger.info("Too many weeks")
        raise BadRequestDataException(
            message="Too many weeks", status_code=status.HTTP_400_BAD_REQUEST
        )


def check_task_result_status(task_result: AsyncResult) -> None:
    for child_result in task_result.children:
        if not child_result.ready():
            app_logger.info("Task is pending")
            raise CeleryException(
                message="Task is pending", status_code=status.HTTP_202_ACCEPTED
            )
        elif child_result.failed():
            app_logger.info(f"task ID {child_result.id} ")
            raise CeleryException(
                message="Task failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
