import pytest_asyncio

from authentication.security import get_password_hash
from models.users import User


@pytest_asyncio.fixture(scope="function", autouse=True)
async def user(async_db_session) -> None:
    user = User(
        name="fourth_user",
        email="fourth@user.com",
        password=get_password_hash("<PASSWORD4>"),
    )
    async_db_session.add(user)
    await async_db_session.flush()
