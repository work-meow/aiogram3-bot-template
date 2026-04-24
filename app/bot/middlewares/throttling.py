from typing import Any
from loguru import logger
from cachetools import TTLCache
from aiogram import BaseMiddleware
from collections.abc import Awaitable, Callable
from aiogram.types import TelegramObject, Message, CallbackQuery


Handler = Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]]

class ThrottlingMiddleware(BaseMiddleware):
    """Антиспам: ограничение частоты запросов."""

    def __init__(self, rate_limit: float = 0.5) -> None:
        # Автоматически удаляет юзеров из кэша через 0.5 секунд
        self.cache: TTLCache[int, bool] = TTLCache(maxsize=10_000, ttl=rate_limit)

    async def __call__(
        self,
        handler: Handler,
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:

        # 1. Фильтр: защищаем только сообщения и клики (и отсекаем посты от каналов)
        if not isinstance(event, (Message, CallbackQuery)) or not event.from_user:
            return await handler(event, data)

        # 2. Проверка на флуд
        u_id = event.from_user.id
        if u_id in self.cache:
            logger.debug(f"🛑 SPAM DROP | User: {u_id}")
            return None

        # 3. Фиксация действия
        self.cache[u_id] = True

        # 4. Пропускаем апдейт дальше
        return await handler(event, data)