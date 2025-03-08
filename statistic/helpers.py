from datetime import date, timedelta
from typing import List, Tuple, Dict


def generate_date_ranges(weeks_count: int) -> List[Tuple[date, date]]:
    date_ranges: List = []
    start_date: date = date.today() - timedelta(weeks=weeks_count)
    dt_gt: date = start_date
    dt_lt: date = start_date + timedelta(days=6)
    while dt_lt <= date.today():
        date_ranges.append((dt_gt, dt_lt))
        dt_gt += timedelta(days=7)
        dt_lt += timedelta(days=7)

    date_ranges.reverse()

    return date_ranges


def format_metrics_response(
    date_range: List[Tuple[date, date]],
    metric_name: str,
    metric_values: List[int],
) -> List[Dict[str, str]]:
    response_data: List[dict] = []
    for index, date_range in enumerate(date_range):
        start_date, end_date = date_range
        response_data.append(
            {
                "start_date": start_date,
                "end_date": end_date,
                metric_name: str(metric_values[index]),
            }
        )
