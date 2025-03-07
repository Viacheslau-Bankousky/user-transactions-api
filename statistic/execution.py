from typing import List

from celery.result import AsyncResult
from fastapi import status

from exceptions.celery import CeleryException
from schemas.statistic import ResponseStatisticModel


async def execute_tasks_chain(tasks_chain, statistic_results: List) -> None:
    try:
        statistic_result = tasks_chain.apply_async()
        statistic_response: ResponseStatisticModel = await AsyncResult(
            statistic_result.id
        ).get(timeout=30)
        statistic_results.append(statistic_response)
    except TimeoutError:
        raise CeleryException(
            message="Celery task timeout error",
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        )
    except Exception:
        raise CeleryException(
            message="Celery task error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
