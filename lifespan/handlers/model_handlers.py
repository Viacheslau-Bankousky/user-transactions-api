"""
This module manages the loading and initialization of application models.

The `ModelLoader` class, which extends `ApplicationEventHandler`,
handles tasks related to application models. During application startup,
it establishes a connection to the appropriate database engine (based on the
environment) and initializes the metadata for the models. During application
shutdown, it performs cleanup tasks, including logging the shutdown process
and disposing of the database engine connection.
"""
from core.models import Base
from core.database import engine as engine
from core.logger_configuration import app_logger
from lifespan.handlers.abstract_handlers import ApplicationEventHandler


class ModelLoader(ApplicationEventHandler):
    """
    Manages the initialization and cleanup processes for application models.

    This class extends the `ApplicationEventHandler` and implements its
    abstract methods to ensure models are correctly loaded and initialized
    during application startup and properly shutdown during the cleanup
    process.
    """

    async def startup(self) -> None:
        """Perform tasks during application startup.

        - Establish a connection to the correct database engine.
        - Initialize application model metadata.
        - Log the beginning of the model initialization process.
        """
        async with engine.begin() as connection:
            app_logger.info("Model Loader Started")
            await connection.run_sync(Base.metadata.create_all)

    async def shutdown(self) -> None:
        """Execute tasks during application shutdown.

        - Logs the shutdown process.
        - Disposes of the database engine connection.
        """
        app_logger.info("Model Loader Stopped")
        await engine.dispose()
