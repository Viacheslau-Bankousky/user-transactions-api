from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore


class Settings(BaseSettings):
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
