"""
Module for performing user-related operations with SQLAlchemy ORM.

This module provides utility functions for querying, creating, and updating
user data in the database.
It leverages SQLAlchemy's ORM and FastAPI data models to perform common
operations such as filtering, ordering, and handling data integrity issues.
The module supports asynchronous database operations to ensure scalability
and modern application design.
"""

from typing import Sequence, Tuple

from fastapi import status
from sqlalchemy import Result, Select, Update, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import subqueryload

from exceptions.users import UserAlreadyExistsException
from models.users import User, UserBalance
from operations.users import apply_filters
from schemas.transactions import CurrencyEnum
from schemas.users import RequestUserModel, RequestUserUpdateModel


def prepare_filtered_user_query(**filter_params) -> Select[Tuple[User]]:
    """
    Prepare a filtered SQLAlchemy query for retrieving users.

    Args:
        filter_params: Arbitrary keyword arguments representing filters
                        to be applied to the query.

    Returns:
        Select[Tuple[User]]: A filtered SQLAlchemy query for selecting users.
    """
    initial_query: Select[Tuple[User]] = select(User)
    modified_query: Select[Tuple[User]] = build_query(
        query=initial_query,
        **filter_params,
    )
    return modified_query


async def take_users(session: AsyncSession, **filter_params) -> Sequence[User]:
    """
    Retrieve a list of users from the database based on specified filters.

    Args:
        session (AsyncSession): The asynchronous SQLAlchemy session to
            interact with the database.
        filter_params: Arbitrary keyword arguments representing filters
            to be applied to the query.

    Returns:
        Sequence[User]: A list of users matching the specified filters.
    """
    query: Select[Tuple[User]] = prepare_filtered_user_query(**filter_params)
    users: Result[Tuple[User]] = await session.execute(query)
    return users.scalars().all()


async def take_user(session: AsyncSession, **filter_params) -> User | None:
    """
    Retrieve a single user from the database based on specified filters.

    Args:
        session (AsyncSession): The asynchronous SQLAlchemy session to
            interact with the database.
        filter_params: Arbitrary keyword arguments representing filters
            to be applied to the query.

       Returns:
           User | None: The user matching the specified filters,
                or None if no user is found.
    """
    query: Select[Tuple[User]] = prepare_filtered_user_query(**filter_params)
    user: Result[Tuple[User]] = await session.execute(query)
    return user.scalars().first()


def build_query(
    query: Select[Tuple[User]],
    **filter_params,
) -> Select[Tuple[User]]:
    """
    Modify a SQLAlchemy query by applying filters and ordering.

    Args:
        query (Select[Tuple[User]]): The initial SQLAlchemy query object.
        filter_params: Arbitrary keyword arguments representing filters
            to be applied to the query.

    Returns:
        Select[Tuple[User]]: The modified query with applied filters and
            ordering.
    """
    if filter_params:
        query = apply_filters(query=query, **filter_params)
    ordered_query = query.order_by(User.created.desc()).options(
        subqueryload(User.user_balance).load_only(
            UserBalance.currency,
            UserBalance.amount,
        ),
    )
    return ordered_query


async def create_user(session: AsyncSession, user: RequestUserModel) -> User:
    """
    Create a new user in the database and initializes their balances.

    Args:
        session (AsyncSession): The asynchronous SQLAlchemy session
            to interact with the database.
        user (RequestUserModel): The user data required to create
            the new user.

       Raises:
           UserAlreadyExistsException: If the user already exists
            in the database.

       Returns:
           User: The newly created user with initialized balances.
    """
    try:
        new_user = User(**user.model_dump(exclude_unset=True))
        session.add(new_user)
        await session.flush()
    except IntegrityError:
        raise UserAlreadyExistsException(
            status_code=status.HTTP_409_CONFLICT,
            message="User already exists",
        )
    user_balance = [
        UserBalance(user_id=new_user.id, currency=currency.value)
        for currency in CurrencyEnum
    ]
    session.add_all(user_balance)
    await session.flush()
    return new_user


async def update_user(
    session: AsyncSession,
    user_id: int,
    user_data: RequestUserUpdateModel,
) -> User | None:
    """
    Update an existing user's details in the database.

    Args:
        session (AsyncSession): The asynchronous SQLAlchemy session
            to interact with the database.
        user_id (int): The ID of the user to be updated.
        user_data (RequestUserUpdateModel): The user data to update.

    Returns:
        User | None: The updated user instance, or None if the user
            does not exist.
    """
    query: Update = (
        update(User)
        .where(User.id == user_id)
        .values(**user_data.model_dump(exclude_unset=True))
        .returning(User)
    )
    updated_user: Result[Tuple[User]] = await session.execute(query)
    return updated_user.scalars().first()


# async def get_registered_users_count(
#     session: AsyncSession, dt_gt: date, dt_lt: date
# ):
#     q = select(User).where(
#         (func.date(User.created >= dt_gt)) & (func.date(User.created) <= dt_lt)
#     )
#     registered_users = await session.execute(q)
#     registered_users = registered_users.fetchall()
#     return len(registered_users)
#
#
# async def get_registered_and_deposit_users_count(
#     session: AsyncSession, dt_gt: date, dt_lt: date
# ):
#     result = 0
#     q = select(User).where(
#         (func.date(User.created) >= dt_gt) & (func.date(User.created) <= dt_lt)
#     )
#     registered_users = await session.execute(q)
#     registered_users = registered_users.scalars()
#     for user in registered_users:
#         q = select(Transaction).where(
#             (func.date(Transaction.created) >= dt_gt)
#             & (func.date(Transaction.created) <= dt_lt)
#             & (Transaction.user_id == user.id)
#             & (Transaction.amount > 0)
#         )
#         deposits = await session.execute(q)
#         deposits = deposits.fetchall()
#         if len(deposits) > 0:
#             result += 1
#     return result
