"""
Module for creating statistic responses.

This module provides Celery tasks to create responses for statistics
calculated over specific date ranges. It combines multiple metrics into
a structured response for both individual date ranges and aggregated
results over multiple ranges.

Key Features:
- **Single Date Range Response**: Combines metrics into a response for a
  specific date range.
- **Aggregated Response**: Aggregates metrics from multiple date ranges
  into a single list of responses.

Dependencies:
- Requires Celery for task orchestration.

Tasks:
- **create_statistic_response**: Creates a response for a single
 date range.
- **create_final_statistic_response**: Aggregates responses for
 all date ranges.
"""

from datetime import date
from typing import Dict, List

from core.celery_app import app


@app.task
def create_statistic_response(
    metrics: List[Dict[str, str | int]], dt_gt: date, dt_lt: date
) -> Dict[str, str | int]:
    """
    Create a response for a specific date range by combining metrics.

    Args:
        metrics (List[Dict[str, str | int]]): A list of metrics,
            where each metric is represented as a dictionary.
        dt_gt (date): Start date of the range.
        dt_lt (date): End date of the range.

    Returns:
        Dict[str, str | int]: A dictionary containing the `start_date`,
            `end_date`, and combined metrics.

    Workflow:
        - Adds the start and end dates (`dt_gt` and `dt_lt`) to the
            response.
        - Updates the response with all provided metrics.

    Example:
        metrics = [{"registered_users": 100}, {"transactions": 50}]
        response = create_statistic_response(
        metrics, date(2023, 1, 1), date(2023, 1, 7)
        )
        # Output: {
        #          "start_date": "2023-01-01",
        #          "end_date": "2023-01-07",
        #          "registered_users": 100,
        #          "transactions": 50
        #          }
    """
    response_data: Dict = {}
    response_data.update({"start_date": str(dt_gt), "end_date": str(dt_lt)})

    for metric in metrics:
        response_data.update(metric)

    return response_data


@app.task
def create_final_statistic_response(
    statistic_result: List[Dict[str, str | int]]
) -> List[Dict[str, str | int]]:
    """
    Aggregate responses from multiple date ranges.

    Args:
        statistic_result (List[Dict[str, str | int]]): A list of responses,
            where each item is a dictionary containing all metrics
            for a specific date range.

    Returns:
        List[Dict[str, str | int]]: A list of dictionaries, where each
        dictionary represents the aggregated metrics for a date range.

    Workflow:
        - Accepts the individual responses for each date range.
        - Returns them in the form of a list.

    Example:
        statistic_result = [
            {
            "start_date": "2023-01-01",
            "end_date": "2023-01-07",
            "transactions": 50
            },
            {
            "start_date": "2023-01-08",
            "end_date": "2023-01-14",
            "transactions": 60
            },
        ]
        response = create_final_statistic_response(statistic_result)
        # Output: [
        #             {
        #             "start_date": "2023-01-01",
        #             "end_date": "2023-01-07",
        #             "transactions": 50
        #             },
        #             {
        #             "start_date": "2023-01-08",
        #             "end_date": "2023-01-14",
        #             "transactions": 60
        #             },
        #         ]
    """
    return statistic_result
