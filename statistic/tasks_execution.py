from typing import Dict, List

from fastapi import status

from core.logger_configuration import app_logger
from exceptions.celery import CeleryException
from schemas.statistic import ResponseStatisticModel


def execute_tasks_chain(tasks_chain) -> List[ResponseStatisticModel]:
    try:
        statistic_response: List[Dict] = tasks_chain.apply_async().get(
            timeout=15
        )
        return [
            ResponseStatisticModel(**periodic_statistic)
            for periodic_statistic in statistic_response
        ]
    except TimeoutError:
        app_logger.error("Celery task timeout error")
        raise CeleryException(
            message="Celery task timeout error",
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        )
    except Exception as ex:
        app_logger.error(f"Celery task error: {ex}")
        raise CeleryException(
            message="Celery task error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
