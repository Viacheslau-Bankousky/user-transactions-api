from typing import List

from fastapi import status

from exceptions.celery import CeleryException
from schemas.statistic import ResponseStatisticModel
from core.logger_configuration import app_logger

# def execute_tasks_chain(tasks_chain, statistic_results: List) -> None:
#     try:
#         statistic_result = tasks_chain.apply_async()
#         statistic_response: ResponseStatisticModel = statistic_result.get(timeout=15)
#         statistic_results.append(statistic_response)
#     except TimeoutError:
#         app_logger.error("Celery task timeout error")
#         raise CeleryException(
#             message="Celery task timeout error",
#             status_code=status.HTTP_504_GATEWAY_TIMEOUT,
#         )
#     except Exception as ex:
#         app_logger.error(f"Celery task error: {ex}")
#         raise CeleryException(
#             message="Celery task error",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )

def execute_tasks_chain(tasks_chain, statistic_results: List) -> None:
    try:
        statistic_result = tasks_chain.apply_async()
        statistic_response = statistic_result.get(timeout=15)
        statistic_results.append(statistic_response)
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