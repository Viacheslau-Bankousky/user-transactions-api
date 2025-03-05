"""
This module defines API routes for managing user data in the application.

It provides functionality to perform CRUD operations on users stored in
the database.
The routes utilize FastAPI framework and integrate with SQLAlchemy for
database interactions and custom exception handling for error scenarios.
"""

from typing import Annotated, AsyncContextManager, Sequence, cast

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from authentication.user_management import check_user_has_token
from core.database import get_session
from core.logger_configuration import app_logger
from models.users import User
from operations.users import (
    serialize_user_to_response,
    serialize_users_to_response,
)
from repositories.users import create_user, take_user, take_users, update_user
from schemas.users import (
    RequestUserModel,
    RequestUserUpdateModel,
    ResponseUserModel,
    UserModel,
)
from validators.users import check_user_exists, validate_user_status

SESSION_DEPENDENCY = Annotated[
    AsyncContextManager[AsyncSession],
    Depends(get_session),
]

router = APIRouter()


@router.get(
    "/users",
    response_model=Sequence[ResponseUserModel],
    status_code=status.HTTP_200_OK,
    description="Get all users",
    response_description="All users returned successfully",
    dependencies=[Depends(check_user_has_token)],
)
async def get_all_users(
    session_manager: SESSION_DEPENDENCY,
) -> Sequence[ResponseUserModel]:
    """
    Fetch all users from the database.

    This endpoint retrieves the complete list of users stored in the
    database and serializes them into response models.

    Args:
        session_manager (SESSION_DEPENDENCY): SQLAlchemy asynchronous
            session dependency used for interacting with the database.

    Returns:
        Sequence[ResponseUserModel]: A list of serialized users.
    """
    app_logger.info("Received GET request for /users endpoint")
    async with session_manager as session:
        users: Sequence[User] = await take_users(
            session=session,
        )
        app_logger.info(f"Fetched {len(users)} users from database")

    return serialize_users_to_response(data_to_process=users)


@router.get(
    "/users/{user_id:int}",
    response_model=ResponseUserModel,
    status_code=status.HTTP_200_OK,
    description="Get user by email or id",
    response_description="User returned successfully",
    dependencies=[Depends(check_user_has_token)],
)
async def get_user(
    session_manager: SESSION_DEPENDENCY,
    user_id: int,
) -> ResponseUserModel | None:
    """
    Retrieve a user's data by their unique ID.

    This endpoint fetches a single user's details from the database
    based on their ID.
    If the user does not exist, a `UserNotFoundException` is raised.

    Args:
        session_manager (SESSION_DEPENDENCY): SQLAlchemy asynchronous
            session dependency used for interacting with the database.
        user_id (int): The unique ID of the user to fetch.

    Returns:
        ResponseUserModel | None: The serialized user's details.
    """
    app_logger.info(
        f"Received GET request for /users endpoint" f" by id {user_id}",
    )
    async with session_manager as session:
        user: User | None = await take_user(session=session, id=user_id)
        check_user_exists(user=user)
        user = cast(User, user)
        app_logger.info("Fetched a user from database")
        return serialize_user_to_response(data_to_process=user)


@router.get(
    "/users/{user_name:str}",
    response_model=ResponseUserModel,
    status_code=status.HTTP_200_OK,
    description="Get users by name",
    response_description="User returned successfully",
    dependencies=[Depends(check_user_has_token)],
)
async def get_users_by_name(
    session_manager: SESSION_DEPENDENCY,
    user_name: str,
) -> ResponseUserModel | None:
    """
    Retrieve a user's data by their name.

    This endpoint fetches a user from the database based on the
    provided name.
    If the user does not exist, a `UserNotFoundException` is raised.

    Args:
        session_manager (SESSION_DEPENDENCY): SQLAlchemy asynchronous
            session dependency used for interacting with the database.
        user_name (str): The name of the user to fetch.

    Returns:
        ResponseUserModel | None: The serialized user's details.
    """
    app_logger.info("Received GET request for /users endpoint by name")
    async with session_manager as session:
        user: User | None = await take_user(
            session=session,
            name=user_name,
        )
        check_user_exists(user=user)
        user = cast(User, user)
        app_logger.info("Fetched a user from database")
        return serialize_user_to_response(data_to_process=user)


@router.get(
    "/users/status/{user_status:str}",
    response_model=Sequence[ResponseUserModel],
    status_code=status.HTTP_200_OK,
    description="Get users by status",
    response_description="Users returned successfully",
    dependencies=[Depends(check_user_has_token)],
)
async def get_users_by_status(
    session_manager: SESSION_DEPENDENCY,
    user_status: str,
) -> Sequence[ResponseUserModel]:
    """
    Retrieve all users with a specific status.

    This endpoint fetches a list of users from the database that match
    the provided status.
    If the status is invalid, a `UserNotFoundException` is raised.

    Args:
        session_manager (SESSION_DEPENDENCY): SQLAlchemy asynchronous
            session dependency used for interacting with the database.
        user_status (str): The status of users to filter by.

    Returns:
        Sequence[ResponseUserModel]: A list of serialized users with
            the specified status.
    """
    app_logger.info("Received GET request for /users endpoint by status")
    validate_user_status(user_status=user_status)
    async with session_manager as session:
        users: Sequence[User] = await take_users(
            session=session,
            status=user_status,
        )
        app_logger.info(
            f"Fetched {len(users)} users from database"
            f" with status: {user_status}",
        )

        return serialize_users_to_response(data_to_process=users)


@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    description="Create user",
    response_model=UserModel,
    response_description="User created successfully",
    dependencies=[Depends(check_user_has_token)],
)
async def post_user(
    session_manager: SESSION_DEPENDENCY,
    user: RequestUserModel,
):
    """
    Create a new user in the database.

    This endpoint takes valid user data, creates a new user in the database,
    and returns the created user details.

    Args:
        session_manager (SESSION_DEPENDENCY): SQLAlchemy asynchronous
            session dependency used for interacting with the database.
        user (RequestUserModel): The user's data to be created.

    Returns:
        UserModel: The newly created user's details.
    """
    app_logger.info("Received POST request for /users endpoint")
    async with session_manager as session:
        user_in_db: User = await create_user(session=session, user=user)
        app_logger.info(
            f"User with email {user_in_db.email} created successfully",
        )
    return user_in_db


@router.patch(
    "/users/{user_id:int}",
    response_model=UserModel | None,
    status_code=status.HTTP_200_OK,
    description="Update user",
    response_description="User updated successfully",
    dependencies=[Depends(check_user_has_token)],
)
async def patch_user(
    session_manager: SESSION_DEPENDENCY,
    user_id: int,
    user: RequestUserUpdateModel,
):
    """
    Update details for an existing user.

    This endpoint updates a user's details in the database based on
    the provided ID and partial user data.
    If the user is not found, a `UserNotFoundException` is raised.

    Args:
        session_manager (SESSION_DEPENDENCY): SQLAlchemy asynchronous
            session dependency used for interacting with the database.
        user_id (int): The unique ID of the user to update.
        user (RequestUserUpdateModel): Partial data for the user update.

    Returns:
        UserModel | None: The updated user's details.
    """
    app_logger.info(
        f"Received PATCH request for /users endpoint by id {user_id}",
    )
    async with session_manager as session:
        updated_user: User | None = await update_user(
            session=session,
            user_id=user_id,
            user_data=user,
        )
        check_user_exists(user=updated_user)
        updated_user = cast(User, updated_user)
        app_logger.info(f"User with id {user_id} was updated successfully")
        return updated_user
