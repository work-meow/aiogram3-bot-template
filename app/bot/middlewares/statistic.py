from typing import Any
from aiogram import BaseMiddleware
from collections.abc import Awaitable, Callable
from aiogram.types import TelegramObject, Update

from app.metrics import ACTIONS, ERRORS


type EventData = dict[str, Any]
type Handler = Callable[
    [
        TelegramObject,
        EventData
    ],
    Awaitable[Any]
]


class MetricsMiddleware(BaseMiddleware):
    """Запись метрик и аналитика: учет
    действий и перехват сбоев."""

    __slots__ = ()

    async def __call__(
        self,
        handler: Handler,
        event: TelegramObject,
        data: EventData,
    ) -> Any:
        """Перехватывает событие для 
        записи метрик и ошибок."""
        
        # 1. Извлекаем данные из конвейера
        # (action_type берем от ActionMiddleware,
        # items_count от MediaGroupMiddleware)
        action = data.get("action_type", "unknown")
        count = data.get("items_count", 1)
        
        # 2. Увеличиваем счетчик
        # активности (Zero I/O)
        ACTIONS.labels(
            service="bot", 
            action_type=action
        ).inc(count)
        
        try:
            # 3. Передаем событие
            # дальше по нашей цепочке
            return await handler(event, data)
        
        except Exception as exc:
            # 4. Перехватываем и 
            # логируем сбой
            ERRORS.labels(
                service="bot", 
                error_type=type(exc).__name__
            ).inc()
            raise
        
        
        