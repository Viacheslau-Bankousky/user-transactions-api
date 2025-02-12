"""
This module defines the `Transaction` model in the database.

The `Transaction` table is used to track financial transactions associated
with users.
Each transaction includes information such as the user who
initiated it, the currency, the amount, the transaction status, and the
timestamp of when it was created.
"""

from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.types import Enum as SQLAlchemyEnum

from core.models import Base  # type: ignore
from models.enums import CurrencyEnum, TransactionStatusEnum


class Transaction(Base):
    """
    Represents the "transaction" database table.

    Attributes:
        id (Mapped[int]): The primary key of the transaction.
        user_id (Mapped[int]): A foreign key referencing the user who initiated
        the transaction.
        currency (Mapped[CurrencyEnum]): The currency in which the transaction
        was performed.
        amount (Mapped[float]): The amount of the transaction.
        status (Mapped[TransactionStatusEnum]): The status of the transaction
        (e.g., processed, roll_backed).
        created (Mapped[datetime]): Timestamp of when the transaction was
        created.
        owner (Mapped["User"]): Relationship linking the transaction to the
        User who performed it.
    """

    __tablename__ = "transaction"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    currency: Mapped[CurrencyEnum] = mapped_column(
        SQLAlchemyEnum(CurrencyEnum), nullable=False
    )
    amount: Mapped[float]
    status: Mapped[TransactionStatusEnum] = mapped_column(
        SQLAlchemyEnum(TransactionStatusEnum),
        default=TransactionStatusEnum.PROCESSED,
    )
    created: Mapped[datetime] = mapped_column(default=datetime.now())
    owner: Mapped["User"] = relationship(back_populates="user_transactions")  # type: ignore # noqa: F821, E501
