"""
This module provides an Abstract Base Class(ABC) `ApplicationEventHandler`.

It serves as a model for specialized application event handlers.

The `ApplicationEventHandler` class is an ABC that defines a standard
interface for all event handlers.
In particular, it specifies two coroutine methods, `startup` and `shutdown`,
that are expected to be implemented by any concrete subclass.
"""

from abc import ABC, abstractmethod


class ApplicationEventHandler(ABC):
    """Abstract class for handling application events.

    Child classes should implement the `startup` and `shutdown`
    coroutine methods.
    """

    @abstractmethod
    async def startup(self):
        """Execute during application start-up."""
        raise NotImplementedError("This method should be implemented")

    @abstractmethod
    async def shutdown(self):
        """Execute during application shutdown."""
        raise NotImplementedError("This method should be implemented")
