"""
This module provides a configuration class for managing env-based settings.

It is designed to read application configuration details from an `.env`
file and expose properties to retrieve essential environment-specific
URLs and credentials.

The `Settings` class manages the following configuration:
- Database credentials and connection string.
- Application environment (e.g., Production, Testing).
- RabbitMQ credentials for Celery broker configuration.
- Redis URL for Celery backend.

The exported `settings` object is an instance of the `Settings` class,
which handles auto-loading of environment variables and validation of
required settings based on the application's environment.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore


class Settings(BaseSettings):
    """
    A configuration class for managing application settings .

    This class simplifies the process of defining, validating, and accessing
    environment-specific settings. It reads configuration from both `.env`
    files and environment variables, with proper validation to ensure all
    necessary parameters are supplied in the correct environment.

    Attributes:
        DB_USER (str | None): The database username (used in Production).
        DB_PASSWORD (str | None): The database password (used in Production).
        ENVIRONMENT (str): The current application environment. Defaults to
        "Production".
        SECRET_KEY (str | None): A general-purpose secret key for the
        application.
        RABBIT_USER (str | None): The RabbitMQ username for Celery broker.
        RABBIT_PASSWORD (str | None): The RabbitMQ password for Celery broker.
        model_config (SettingsConfigDict): Pydantic configuration specifying
                `.env` file usage and encoding.
    """

    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    ENVIRONMENT: str = "Production"
    SECRET_KEY: str | None = None
    RABBIT_USER: str | None = None
    RABBIT_PASSWORD: str | None = None
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    @property
    def db_url(self) -> str:
        """
        Construct and return the database connection URL depends on the environment.

        Returns:
            str: The database connection URL.

        Raises:
            ValueError: If required environment variables are missing or the
                environment is invalid.
        """
        if self.ENVIRONMENT == "Production":
            if not (self.DB_USER and self.DB_PASSWORD):
                raise ValueError(
                    "DB_USER and DB_PASSWORD must be set in Production"
                )
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@db:5432/internship-task_db"  # noqa: E501
        elif self.ENVIRONMENT == "Testing":
            return "sqlite+aiosqlite:///:memory:"
        else:
            raise ValueError(f"Invalid environment: {self.ENVIRONMENT}")

    @property
    def celery_broker_url(self) -> str:
        """
        Construct and return the Celery broker URL for RabbitMQ.

        This URL is used by Celery to connect to the RabbitMQ broker.

        Returns:
            str: The RabbitMQ broker URL.

        Raises:
            ValueError: If `RABBIT_USER` or `RABBIT_PASSWORD` is not set.
        """
        if not (self.RABBIT_USER and self.RABBIT_PASSWORD):
            raise ValueError(
                "RABBIT_USER and RABBIT_PASSWORD must be set in Production"
            )
        if self.ENVIRONMENT == "Testing":
            return "amqp://guest:guest@rabbitmq:5672//"

        return (
            f"amqp://{self.RABBIT_USER}:{self.RABBIT_PASSWORD}@rabbitmq:5672//"
        )

    @property
    def celery_backend_url(self) -> str:
        """
        Return the Celery backend URL for Redis.

        This is a static property that points to the local Redis instance:
        `redis://redis:6379/0`.

        This URL is used by Celery to store task results.

        Returns:
            str: The Redis backend URL.
        """
        return "redis://redis:6379/0"


settings = Settings()
