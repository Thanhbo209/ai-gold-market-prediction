
"""Application configuration loaded from environment variables."""

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Gold Market Prediction API"
    app_env: str = "development"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"

    database_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_database_url(self) -> "Settings":
        """Validate database configuration for the current environment."""
        if not self.database_url:
            if self.app_env != "development":
                raise ValueError(
                    "DATABASE_URL must be configured outside development."
                )

            self.database_url = (
                "postgresql+psycopg://postgres:postgres@localhost:5432/gold_prediction"
            )

        return self


settings = Settings()
