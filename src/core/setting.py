"""Service settings."""

import os.path
from enum import StrEnum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

from src.core.util.project import ProjectInfo


class EnvironmentType(StrEnum):
    """Types for environment settings."""

    DEVELOPMENT = "dev"
    TEST = "test"
    PRODUCTION = "prod"


class Settings(BaseSettings):
    """Service settings."""

    ENVIRONMENT: EnvironmentType = Field(...)

    EXCLUDE_FIELDS: set[str] = {"id", "created_at", "updated_at"}

    POSTGRES_HOST: str = Field(...)
    POSTGRES_PORT: int = Field(...)
    POSTGRES_DB: str = Field(...)
    POSTGRES_USER: str = Field(...)
    POSTGRES_PASSWORD: str = Field(...)

    # REDIS_HOST: str = Field(...)
    # REDIS_PORT: int = Field(...)
    # REDIS_USER: str = Field(...)
    # REDIS_PASSWORD: str = Field(...)

    @property
    def POSTGRES_URL(self) -> str:
        """PostgreSQL Url."""
        return str(
            URL.build(
                scheme="postgresql+asyncpg",
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                user=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                path=f"/{self.POSTGRES_DB}",
            ),
        )

    # def REDIS_URL(self, database: int = 0) -> str:
    #     """Redis Url."""
    #     return str(
    #         URL.build(
    #             scheme="redis",
    #             host=self.REDIS_HOST,
    #             port=self.REDIS_PORT,
    #             user=self.REDIS_USER,
    #             password=self.REDIS_PASSWORD,
    #             path=f"/{database}",
    #         ),
    #     )

    model_config = SettingsConfigDict(
        case_sensitive=True,
    )


settings = Settings()  # type: ignore[call-arg]
project_info = ProjectInfo(
    main_path=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
)
