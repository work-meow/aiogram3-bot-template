import orjson

from loguru import logger
from typing import Any, Final
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)

from app.storage.events import trace_sql
from app.settings import get_settings
from app.storage.models import *
from app.storage.enums import *



def _json_dumps(obj: Any) -> str:
    """orjson вместо stdlib json."""
    return orjson.dumps(obj).decode()


# 1. Инициализируем пул подключений
engine: Final = create_async_engine(
    url=get_settings().DATABASE_URL,
    pool_size=50,
    max_overflow=20,
    pool_recycle=1800,
    pool_pre_ping=True,
    json_serializer=_json_dumps,
    json_deserializer=orjson.loads,
    echo=False,
)


# 2. Мониторинг запросов
trace_sql(engine.sync_engine)


# 3. Наша фабрика сессий
session_factory: Final = async_sessionmaker(
    class_=AsyncSession,
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


# 4. Пингер для проверки на старте
async def ping_database() -> None:
    """Проверяет соединение 
    с базой данных."""
    
    try:
        async with engine.begin() as conn:
            await conn.scalar(select(1))
        logger.info("⚡ PostgreSQL подключен.")

    except Exception as e:
        logger.error(f"❌ Ошибка конекта к PostgreSQL: {e}")
        raise