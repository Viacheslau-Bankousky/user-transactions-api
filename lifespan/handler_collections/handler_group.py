"""
This module provides a class, 'Handlers', which manages event handlers.

The key offering of this module is the 'Handlers' class.
It maintains a list of various application event handlers and offers
asynchronous methods for starting up and shutting down these handlers.
"""

from typing import List

from lifespan.handlers.abstract_handlers import ApplicationEventHandler
from lifespan.handlers.model_handlers import ModelLoader


class EventHandler:
    """
    A class to represent a collection of application event handlers.

    Attributes
    ----------
    handlers : List[ApplicationEventHandler]
        a list of different application event handlers

    """

    handlers: List[ApplicationEventHandler] = []

    def add_handler(self, event_handler: ApplicationEventHandler) -> None:
        """Add a new handler to the handler's list.

        Args:
            event_handler (ApplicationEventHandler): A handler to add.
        """
        self.handlers.append(event_handler)

    async def startup_all(self) -> None:
        """Start up all handlers in the handlers list asynchronously."""
        for event_handler in self.handlers:
            await event_handler.startup()

    async def shutdown_all(self) -> None:
        """Shut down all handlers in the handlers list asynchronously."""
        for event_handler in self.handlers:
            await event_handler.shutdown()


current_event_handler = EventHandler()
current_event_handler.add_handler(ModelLoader())
