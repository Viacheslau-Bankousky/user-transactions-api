from datetime import date
from typing import Dict, List

from schemas.statistic import ResponseStatisticModel
from statistic.celery_app import app


@app.task
def create_statistic_response(
    tasks_result: List[Dict[str, int | str]], start_date: date, end_date: date
) -> ResponseStatisticModel:
    response_date: Dict = {}
    for metric in tasks_result:
        metric_key: str = list(metric.keys())[0]
        metric_value: int | str = list(metric.values())[0]
        response_date[metric_key] = metric_value
    response = ResponseStatisticModel(
        **response_date, start_date=start_date, end_date=end_date
    )
    return response.model_dump()

