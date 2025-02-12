"""
This module provides a base class for SQLAlchemy ORM models.

This module defines a base class that serves as a foundation for creating
SQLAlchemy ORM models.
It leverages SQLAlchemy's asynchronous functionality, making it suitable
for asynchronous database operations.
"""

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase, AsyncAttrs):
    """
    Abstract base class for SQLAlchemy ORM models with asynchronous support.

    This class combines the `DeclarativeBase` for defining ORM models and
    the `AsyncAttrs` for enabling asynchronous interactions with the
    database. Models inheriting from this base class must define their
    own table structures while inheriting the asynchronous capabilities.

    Attributes:
        __abstract__ (bool): Indicates that this class is abstract and not
        tied to a specific database table.
    """

    __abstract__ = True
