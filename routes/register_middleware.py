"""
Module for registering FastAPI middlewares.

This module provides functionality for adding middlewares.
Middlewares are executed either before processing incoming requests
or after generating responses.

Key features:
- Registers custom middleware for handling HTTP-level errors by wrapping
 requests with error-handling logic.
- Ensures centralized processing of errors using the
 `execute_errors_handling` middleware.

This module simplifies middleware registration and abstracts
 the setup process.
"""

from fastapi import FastAPI

from middlewares.error_handler import execute_errors_handling


def register_middleware(app: FastAPI) -> None:
    """
    Register custom middlewares for the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.

    Details:
        - This function applies the `execute_errors_handling` middleware
            to wrap HTTP requests with centralized error-handling logic.
        - The middleware intercepts requests and responses at the HTTP
            level to process errors globally.

    Usage:
        Call this function during application setup to add the middleware.
    """
    app.middleware("http")(execute_errors_handling)
