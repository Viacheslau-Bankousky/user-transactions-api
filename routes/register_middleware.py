"""
This module contains FastAPI middlewares for the application.

Middlewares are used for processing that needs to be made on
requests or responses, before passing them to any incoming
request or before sending any outgoing responses.
"""
from fastapi import FastAPI

from middlewares.error_handler import execute_errors_handling


def register_middleware(app: FastAPI) -> None:
    app.middleware("http")(execute_errors_handling)
