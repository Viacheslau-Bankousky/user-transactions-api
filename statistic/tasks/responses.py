from datetime import date
from typing import Dict, List

from core.celery_app import app


@app.task
def create_statistic_response(
    metrics: List[Dict[str, str | int]], dt_gt: date, dt_lt: date
) -> Dict[str, str | int]:
    response_data: Dict = {}
    response_data.update({"start_date": str(dt_gt), "end_date": str(dt_lt)})

    for metric in metrics:
        response_data.update(metric)

    return response_data



@app.task
def create_final_statistic_response(
        metrics: List[Dict[str, str | int]]
) -> List[Dict[str, str | int]]:
    return metrics