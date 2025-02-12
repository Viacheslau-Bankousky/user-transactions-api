"""
This module contains FastAPI middlewares for the application.

Middlewares are used for processing that needs to be made on
requests or responses, before passing them to any incoming
request or before sending any outgoing responses.
"""

from typing import Awaitable, Callable

from fastapi import Request, Response

from core.logger_configuration import app_logger
from main import app
from middlewares.error_handler import ErrorHandler


@app.middleware("http")
async def exception_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """
    Handle errors and exceptions.

    This function handles exceptions that occur during the handling
    of a request.
    It is used either to return a response with a specific status
    code or optionally to re-raise exceptions.

    Args:
        request (Request):
            The incoming request.
        call_next (Callable):
            The function to be called next.

    Returns:
        Response: The response of the request if no exception was caught,
        returns an error response otherwise.
    """
    app_logger.info("Running errors handling middleware")
    return await ErrorHandler.handle_errors(request, call_next)
