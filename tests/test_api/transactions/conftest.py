import pytest_asyncio

from tests.utils.test_data_setup import add_transactions, update_user_balances


@pytest_asyncio.fixture(scope="function", autouse=True)
async def transactions(async_db_session) -> None:
    await add_transactions(session=async_db_session)
    await update_user_balances(session=async_db_session)
