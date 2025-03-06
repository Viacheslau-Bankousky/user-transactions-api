from datetime import date
from typing import Tuple, TypeVar

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
    for query_param, query_param_value in filter_params.items():
        if query_param_value:
            query = query.filter(
                getattr(model, query_param) == query_param_value
            )

    return query


def get_date_range_filter(
    date_from: date, date_to: date, model: type[ModelType]
) -> BinaryExpression:
    return (func.date(model.created) >= date_from) & (
        func.date(model.created) <= date_to
    )
