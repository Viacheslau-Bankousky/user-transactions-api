from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from models.enums import CurrencyEnum, TransactionPurposeEnum
from models.transactions import Transaction
from models.users import User, UserBalance
from repositories.users_balances import get_user_balance_for_currency
from schemas.users import UserStatusEnum

REFUND_TRANSACTION_AMOUNT: Decimal = Decimal(1000)
USER_ID: int = 1
BLOCKED_USER_ID: int = 3


async def add_users(session: AsyncSession) -> list[User]:
    """
    Create and add users to the database.

    Args:
        session (AsyncSession): The SQLAlchemy asynchronous session used
            for database operations.

    Returns:
        list[User]: A list of created User objects that were added to the
            database.
    """
    user_list = [
        User(
            name="first_user", email="first@user.com", password="<PASSWORD1>"
        ),
        User(
            name="second_user", email="second@user.com", password="<PASSWORD2>"
        ),
        User(
            name="third_user",
            email="third@user.com",
            password="<PASSWORD3>",
            status=UserStatusEnum.BLOCKED,
        ),
    ]
    session.add_all(user_list)
    await session.flush()
    return user_list


async def add_balances(session: AsyncSession, users: list[User]) -> None:
    """
    Create and add user balance data for each user.

    Args:
        session (AsyncSession): The SQLAlchemy asynchronous session used
            for database operations.
        users (list[User]): A list of User objects for whom the balance
            data will be created and added.
    """
    balances: list[UserBalance] = []
    for user in users:
        balances.extend(
            UserBalance(user_id=user.id, currency=currency)
            for currency in CurrencyEnum
        )
    session.add_all(balances)
    await session.commit()


async def add_transactions(session: AsyncSession) -> None:
    transactions = [
        Transaction(
            user_id=USER_ID,
            currency=CurrencyEnum.USD,
            amount=REFUND_TRANSACTION_AMOUNT,
            purpose=TransactionPurposeEnum.REFUND,
        ),
        Transaction(
            user_id=BLOCKED_USER_ID,
            currency=CurrencyEnum.USD,
            amount=REFUND_TRANSACTION_AMOUNT,
            purpose=TransactionPurposeEnum.REFUND,
        ),
    ]

    session.add_all(transactions)
    await session.flush()


async def update_user_balances(session: AsyncSession) -> None:
    user_balance: UserBalance = await get_user_balance_for_currency(
        session=session, user_id=USER_ID, currency=CurrencyEnum.USD
    )
    user_balance.amount += REFUND_TRANSACTION_AMOUNT
    session.add(user_balance)
    await session.flush()
