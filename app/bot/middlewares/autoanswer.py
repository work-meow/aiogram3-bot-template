import contextlib

from typing import Any
from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramAPIError
from collections.abc import Awaitable, Callable
from aiogram.types import TelegramObject, CallbackQuery


Handler = Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]]

class AutoAnswerMiddleware(BaseMiddleware):
    """Сброс состояния загрузки на инлайн-кнопках."""

    async def __call__(
        self,
        handler: Handler,
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:

        # 1. Только коллбеки
        if not isinstance(event, CallbackQuery):
            return await handler(event, data)

        try:
            # 2. Выполняем хендлер
            return await handler(event, data)

        finally:
            # 3. Безопасно тушим часики
            with contextlib.suppress(TelegramAPIError):
                await event.answer()