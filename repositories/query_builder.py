from datetime import date
from typing import Tuple, TypeVar

"""
This module provides utility functions for building and filtering queries.

The primary purpose of this module is to simplify the process of constructing,
filtering, and ordering SQLAlchemy queries for models such as `User` and
`Transaction`.
It also includes functionality to apply date range filters to queries.

The key functions handle tasks such as preparing a filtered query
(`prepare_filtered_query`), applying filters (`apply_filters`), ordering results
(`order_query`), and generating date range filters (`get_date_range_filter`).
"""
from sqlalchemy import func, select
from sqlalchemy.orm import subqueryload
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import BinaryExpression

from models.transactions import Transaction
from models.users import User, UserBalance

ModelType = TypeVar("ModelType", User, Transaction)


def prepare_filtered_query(
    model: type[ModelType], **filter_params
) -> Select[Tuple[ModelType]]:
    """
    Prepare a filtered and ordered SQLAlchemy query for a given model.

    This function creates an initial query for the given model, applies any
    specified filters, and orders the results as appropriate for the model type.

    Args:
        model (type[ModelType]): The SQLAlchemy model to query (e.g., `User`,
            `Transaction`).
        **filter_params (dict): Key-value pairs representing filtering criteria
            where keys are model attributes and values are the desired filters.

       Returns:
           Select[Tuple[ModelType]]: A SQLAlchemy `Select` query object
           with filters and ordering applied to it.

       Notes:
           - This function delegates filtering and ordering to `build_query`.
    """
    initial_query: Select[Tuple[ModelType]] = select(model)
    modified_query: Select[Tuple[ModelType]] = build_query(
        model=model,
        query=initial_query,
        **filter_params,
    )
    return modified_query


def build_query(
    model: type[ModelType],
    query: Select[Tuple[ModelType]],
    **filter_params,
) -> Select[Tuple[ModelType]]:
    """
    Build a complete query by applying filters and ordering.

    This function allows the combination of multiple filtering parameters
    and applies model-specific ordering rules to the query.

    Args:
        model (type[ModelType]): The model to query (e.g., `User`, `Transaction`).
        query (Select[Tuple[ModelType]]): The initial query object.
        **filter_params (dict): Filtering parameters as key-value pairs.

    Returns:
        Select[Tuple[ModelType]]: A query that incorporates applied filters
            and ordering specific to the given model.
    """
    if filter_params:
        query = apply_filters(model=model, query=query, **filter_params)
    ordered_query: Select[Tuple[ModelType]] = order_query(
        model=model, query=query
    )

    return ordered_query


def order_query(
    model: type[ModelType],
    query: Select[Tuple[ModelType]],
) -> Select[Tuple[ModelType]]:
    """
    Apply model-specific ordering to a query.

    Args:
        model (type[ModelType]): The model to query for ordering (e.g., `User`,
         `Transaction`).
        query (Select[Tuple[ModelType]]): The query object to be ordered.

    Returns:
        Select[Tuple[ModelType]]: The query ordered based on the model's fields.
    """
    if model == User:
        return query.order_by(User.created.desc()).options(
            subqueryload(User.user_balance).load_only(
                UserBalance.currency,
                UserBalance.amount,
            ),
        )
    elif model == Transaction:
        return query.order_by(Transaction.created.desc())

    return query


def apply_filters(
    model: type[ModelType],
    query: Select[Tuple[ModelType]],
    **filter_params,
) -> Select[Tuple[ModelType]]:
    """
    Apply filtering criteria to a query based on provided parameters.

    Args:
        model (type[ModelType]): The model to query and filter (e.g., `User`,
         `Transaction`).
        query (Select[Tuple[ModelType]]): The query object to filter.
        **filter_params (dict): Filtering parameters where keys are model attributes
            and values are the required matching values.

    Returns:
        Select[Tuple[ModelType]]: A query with the specified filters applied.
    """

    for query_param, query_param_value in filter_params.items():
        if query_param_value:
            query = query.filter(
                getattr(model, query_param) == query_param_value
            )

    return query


def get_date_range_filter(
    date_from: date, date_to: date, model: type[ModelType]
) -> BinaryExpression:
    """
    Generate a date range filter expression for a model's `created` field.

    Args:
        date_from (date): The start date of the range.
        date_to (date): The end date of the range.
        model (type[ModelType]): The model to apply the date range filter.

    Returns:
        BinaryExpression: A SQLAlchemy binary expression for filtering the
        `created` field within the specified date range.

    """
    return (func.date(model.created) >= date_from) & (
        func.date(model.created) <= date_to
    )
