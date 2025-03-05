"""
This module defines the `User` and `UserBalance` models.

Overview:
---------
The `User` model represents a user in the application, storing their ID,
email,status, and associated relationships like balances and transactions.
The `UserBalance` model represents the balances of users in specific
currencies, ensuring that each user can only have one balance per currency.
"""

from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.types import Enum as SQLAlchemyEnum
from sqlalchemy.types import Numeric

from core.constants import PRECISION, SCALE
from core.models import Base  # type: ignore
from models.enums import CurrencyEnum, UserStatusEnum
from models.transactions import Transaction

DEFAULT_AMOUNT: Decimal = Decimal(0)


class User(Base):
    """
    Represents the "user" database table.

    Attributes:
        id (Mapped[int]): The primary key of the user.
        email (Mapped[str | None]): The user's email address (must be unique).
        status (Mapped[UserStatusEnum]): The status of the user
        (e.g., active, blocked).
        created (Mapped[datetime]): Timestamp of when the user entry was
        created.
        user_balance (Mapped[List["UserBalance"]]): Relationship with the
        UserBalance table. Stores all balances belonging to this user.
        user_transactions (Mapped[List["Transaction"]]): Relationship with the
        password (Mapped[str]): The user's password.'
        Transaction table. Stores all transactions related to this user.
    """

    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str | None] = mapped_column(nullable=True, unique=True)
    status: Mapped[UserStatusEnum] = mapped_column(
        SQLAlchemyEnum(UserStatusEnum), default=UserStatusEnum.ACTIVE
    )
    created: Mapped[datetime] = mapped_column(default=datetime.now)
    user_balance: Mapped[List["UserBalance"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
        order_by="UserBalance.amount.desc()",
    )
    user_transactions: Mapped[List[Transaction]] = relationship(  # type: ignore # noqa: F821, E501
        back_populates="owner", cascade="all, delete-orphan"
    )
    password: Mapped[str] = mapped_column(nullable=False)


class UserBalance(Base):
    """
    Represents the "user_balance" database table.

    Attributes:
        id (Mapped[int]): The primary key of the user balance entry.
        user_id (Mapped[int]): A foreign key referencing the user this
        balance belongs to.
        currency (Mapped[CurrencyEnum]): The currency of the balance
        (e.g., USD, EUR ...).
        amount (Mapped[float]): The amount of money in the specified
        currency.
        created (Mapped[datetime]): Timestamp of when the balance entry
        was created.
        owner (Mapped["User"]): Relationship linking the balance to the
        User who owns it.

    Table Constraints:
        A unique constraint (user_id, currency) ensures that each user
        can have only one balance per currency.
    """

    __tablename__ = "user_balance"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    currency: Mapped[CurrencyEnum] = mapped_column(
        SQLAlchemyEnum(CurrencyEnum), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=PRECISION, scale=SCALE), default=DEFAULT_AMOUNT
    )
    created: Mapped[datetime] = mapped_column(default=datetime.now)
    owner: Mapped["User"] = relationship(
        back_populates="user_balance", lazy="joined"
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "currency", name="user_balance_user_currency_unique"
        ),
    )
