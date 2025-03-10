from datetime import date
from typing import Dict, List, Tuple

from core.celery_app import app


@app.task
def create_statistic_response(
    metrics: List[List[Dict[str, str]]], date_ranges: List[Tuple[date, date]]
) -> List[Dict[str, str]]:
    response_data: List[Dict] = []
    for date_range in date_ranges:
        dt_gt, dt_lt = date_range
        response_data.append(
            {"start_date": str(dt_gt), "end_date": str(dt_lt)}
        )

    for metric in metrics:
        for index, metric_data in enumerate(metric):
            response_data[index].update(metric_data)

    return response_data
