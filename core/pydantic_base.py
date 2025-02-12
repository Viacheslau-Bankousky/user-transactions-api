"""
This module provides a base model for constructing pydantic models.

It sets up a configuration to allow attributes to be populated directly
from ORM models, enabling seamless integration between databases and
Pydantic models for responses.
"""

from pydantic import BaseModel, ConfigDict


class BasePydanticModel(BaseModel):
    """
    A base class for Pydantic models.

    This class facilitates the use of ORM models as data sources
    for pydantic models by enabling the `from_attributes=True`
    configuration.
    """

    model_config = ConfigDict(from_attributes=True)
