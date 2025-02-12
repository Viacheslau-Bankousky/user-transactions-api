"""
Module to initialize and configure the testing FastAPI application.

This module sets up the testing FastAPI application instance and includes
the necessary routers for extending application functionality.
In this case, it registers the user-related routes from the `users` module.

Attributes:
    testing_app (FastAPI): The FastAPI application instance.
"""

from fastapi import FastAPI

from routes.users import router as user_router

testing_app = FastAPI()

testing_app.include_router(user_router)
