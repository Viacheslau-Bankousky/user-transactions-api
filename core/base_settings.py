"""
This module handles the loading of environment variables from a `.env` file.

It uses `pydantic.BaseSettings` to access variables defined in the `.env` file
or the system environment.
This approach ensures the application securely manages sensitive information
such as the database username, password, and application execution environment.

Key Components:
- `DB_USER`: Represents the database username. Retrieved from the `DB_USER`
  environment variable. Defaults to `None` if not set.
- `DB_PASSWORD`: Represents the database password. Retrieved from the
  `DB_PASSWORD` environment variable. Defaults to `None` if not set.
- `ENVIRONMENT`: Specifies the application's execution environment
  (e.g., "Production", "Testing"). Defaults to `"Production"` if not set.

Functionality:
- In the `"Production"` environment:
  Constructs the database URL using the provided `DB_USER` and `DB_PASSWORD`
  and raises a `ValueError` if either is missing.
- In the `"Testing"` environment:
  Provides an in-memory SQLite database URL for testing purposes.
- For unsupported environments:
  Raises a `ValueError`.

Usage:
1. Create a `.env` file in the root directory of the project with the desired
   variables, e.g.:
   ```
   DB_USER=your_username
   DB_PASSWORD=your_password
   ENVIRONMENT=Production
   ```

2. Use the `Settings` class to retrieve the configuration values and database
   connection URL.

Notes:
- If the `.env` file is missing or any required variables are not defined,
  default values will be used where possible (e.g., `None` or `"Production"`).
- Avoid committing the `.env` file to version control to ensure secure
  management of sensitive information.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore


class Settings(BaseSettings):
    """
    Represents the application's configuration settings.

    The `Settings` class uses `pydantic.BaseSettings` to load environment
    variables from a `.env` file or the system environment. It provides
    access to configurations such as database credentials (`DB_USER` and
    `DB_PASSWORD`) and the application's execution environment
    (`ENVIRONMENT`).

    Attributes:
        DB_USER (str | None): The database username. Defaults to `None`
        if not set.
        DB_PASSWORD (str | None): The database password. Defaults to
        `None` if not set.
        ENVIRONMENT (str): The execution environment. Defaults to
        `"Production"`
            if not otherwise specified.
        model_config (SettingsConfigDict): The configuration dict for
        loading environment variables from the `.env` file with
        UTF-8 encoding.

    Methods:
        db_url: Generates the database connection URL based on the current
        environment.

    Raises:
        ValueError: If required credentials (`DB_USER` or `DB_PASSWORD`)
        are missing in the `"Production"` environment, or if an invalid
        environment is specified.
    """

    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    ENVIRONMENT: str = "Production"
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    @property
    def db_url(self) -> str:
        """
        Generates the database connection URL based on the current environment.

        In the `"Production"` environment:
            Constructs a PostgreSQL database URL using `DB_USER` and
            `DB_PASSWORD`.
            Raises a `ValueError` if either `DB_USER` or `DB_PASSWORD`
            is missing.

        In the `"Testing"` environment:
            Returns an in-memory SQLite database URL for testing purposes.

        Returns:
            str: The database connection URL.

        Raises:
            ValueError: If either required credentials are missing in the
                `"Production"` environment, or if the `ENVIRONMENT` is not
                `"Production"` or `"Testing"`.
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


settings = Settings()
