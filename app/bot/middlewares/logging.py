from typing import Any
from loguru import logger
from aiogram import BaseMiddleware
from collections.abc import Awaitable, Callable
from aiogram.types import TelegramObject, Update, User


Handler = Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]]

class LoggingMiddleware(BaseMiddleware):
    """Сбор контекста и логгирование апдейта."""

    async def __call__(
        self,
        handler: Handler,
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:

        # 1. Только корневой Update
        if not isinstance(event, Update):
            return await handler(event, data)


        # 2. Получаем метрики
        inner = event.event
        uid: int = event.update_id
        etype: str = event.event_type
        user: User | None = getattr(inner, "from_user", None)
        u_id: int | str = user.id if user else "none"


        # 3. Сбор полезной нагрузки
        payload = ""
        if etype == "callback_query":
            payload = f" | Data: {getattr(inner, 'data', 'empty')}"

        elif etype == "inline_query":
            payload = f" | Qry: {getattr(inner, 'query', 'empty')[:30]}"


        # 4. Определение FSM
        state_name = "default"
        if state := data.get("state"):
            if cur_state := await state.get_state():
                state_name = cur_state


        # 5. Входной лог с полным контекстом
        logger.debug(f"▶ IN  | Upd: {uid} | {etype} | User: {u_id} | State: {state_name}{payload}")

        try:
            # 6. Передача управления дальше по цепочке
            return await handler(event, data)

        finally:
            # 7. Гарантированная фиксация выхода
            logger.debug(f"✅ OUT | Upd: {uid}")