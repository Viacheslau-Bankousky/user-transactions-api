"""
This module contains utilities for serializing user data into response models.

These utilities are used to transform database objects into client-facing
models and to streamline query filtering for users.
"""

from typing import Sequence

from models.users import User
from schemas.users import ResponseUserBalanceModel, ResponseUserModel


def serialize_user_to_response(
    data_to_process: User,
) -> ResponseUserModel:
    """
    Serialize a single `User` database object into a `ResponseUserModel`.

    Args:
        data_to_process (User): The `User` object to be serialized.

    Returns:
        ResponseUserModel: The serialized response model.
    """
    return map_user_to_response_model(user=data_to_process)


def serialize_users_to_response(
    data_to_process: Sequence[User],
) -> Sequence[ResponseUserModel]:
    """
    Serialize `User` database objects into a list of `ResponseUserModel`.

    Args:
        data_to_process (Sequence[User]): A sequence of `User` objects
            to be serialized.

    Returns:
        Sequence[ResponseUserModel]: A list of serialized response models.
            Excludes any `None` values.
    """
    return [
        map_user_to_response_model(user=user)
        for user in data_to_process
        if user is not None
    ]


def map_user_to_response_model(
    user: User,
) -> ResponseUserModel:
    """
    Map a single `User` database object to a `ResponseUserModel`.

    Args:
        user (User): The `User` object to map.

    Returns:
        ResponseUserModel: The mapped response model, including user
            details and their associated balances.
    """
    return ResponseUserModel(
        id=user.id,
        name=user.name,
        email=user.email,
        status=user.status,
        created=user.created,
        balances=[
            ResponseUserBalanceModel(
                currency=balance.currency,
                amount=balance.amount,
            )
            for balance in user.user_balance
        ],
    )
