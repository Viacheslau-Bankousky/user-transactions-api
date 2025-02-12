"""
This module provides an asynchronous context manager for managing the lifespan.

The main functionality of this module is provided by the function `lifespan`,
which handles the application startup and shutdown stages.
The `startup_all` method from the handlers is called before entering
the context, followed by the `shutdown_all` method after leaving
the context.

The module utilizes the `asynccontextmanager` decorator from the contextlib,
and involves the handlers module from the package
`internship-task.lifespan.handler_collections.handler_group`.

Functions:
----------
async def lifespan(_app: FastAPI) -> None:
    Context manager used to handle the application lifespan.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from lifespan.handler_collections.handler_group import current_event_handler


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle the lifespan of the FastAPI application.

    Before entering the context, it calls the startup_all() method
    of the handlers.
    After leaving the context, it calls the shutdown_all() method
    of the handlers.

    Args:
        _app (FastAPI): The FastAPI application instance.

    Yields:
        This context manager does not yield any value.
        However, the use of 'yield' serves to mark the
        context of the application lifespan, with setup
        on entrance (before yield) and shutdown procedures
        on exit (after yield).
    """
    await current_event_handler.startup_all()
    yield
    await current_event_handler.shutdown_all()
