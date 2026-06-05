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
    
    # Enviroment
    APP_ENV: Literal[
        "dev",
        "prod"
    ] = "dev"

    # Web
    WEB_URL: str
    WEB_PORT: int = 8000
    WEB_HOST: str = "0.0.0.0"
    
    # Bot
    BOT_TOKEN: str
    BOT_PROXY: bool = False
    CHANNEL_ID: str | None = None
    BOT_SECRET: str | None = None
    BOT_MODE: Literal[
        "polling", 
        "webhook"
    ] = "polling"
    
    
    # PostgreSQL
    DATABASE_URL: str
    
    # Proxy
    PROXY_URL: str | None = None

    # Logging
    LOG_LEVEL: str = "INFO"
    LOKI_URL: str | None = None
    LOKI_USER: str | None = None
    LOKI_PASS: str | None = None
    LOG_CHAT: str | None = None
    
    
    @computed_field
    @property
    def SRVC_NAME(self) -> str:
        """Динамически формирует имя сервиса"""
        return f"service-name-{self.APP_ENV}"


@cache
def get_settings() -> Settings:
    return Settings()
