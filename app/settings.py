from typing import Literal
from functools import cache
from pydantic import computed_field
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

    # Bot
    BOT_TOKEN: str
    BOT_PROXY: bool = False
    CHANNEL_ID: str | None = None

    # Proxy
    PROXY_URL: str | None = None

    # PostgreSQL
    DATABASE_URL: str

    # Logging & Loki
    LOG_LEVEL: str = "INFO"
    LOKI_URL: str | None = None
    LOKI_USER: str | None = None
    LOKI_PASS: str | None = None
    LOG_CHAT: str | None = None

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
