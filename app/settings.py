from typing import Literal
from functools import cache
from pydantic import Field, computed_field
from pydantic_settings import (
    SettingsConfigDict,
    BaseSettings
)


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_file=".env",
        extra="ignore",
    )

    # Server
    API_TOKEN: str
    API_PORT: int = Field(8080, ge=1, le=65535)
    API_HOST: str = "0.0.0.0"

    # Bot
    BOT_TOKEN: str
    CHANNEL_ID: str | None = None

    # PostgreSQL
    DATABASE_URL: str

    # Logging & Loki
    LOG_LEVEL: str = "INFO"
    LOKI_URL:  str | None = None
    LOKI_USER: str | None = None
    LOKI_PASS: str | None = None
    LOG_CHAT:  str | None = None

    # Enviroment
    APP_ENV: Literal["dev", "prod"] = "dev"

    @computed_field
    @property
    def SRVC_NAME(self) -> str:
        """Динамически формирует имя сервиса"""
        return f"service-name-{self.APP_ENV}"


@cache
def get_settings() -> Settings:
    return Settings()