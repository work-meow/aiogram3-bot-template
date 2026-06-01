import contextlib

from typing import Any
from loguru import logger
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from collections.abc import Awaitable, Callable
from aiogram.types import (
    TelegramObject,
    CallbackQuery,
    InlineQuery,
    Update,
)


type EventData = dict[str, Any]
type Handler = Callable[
    [
        TelegramObject,
        EventData
    ],
    Awaitable[Any]
]


class LoggingMiddleware(
    BaseMiddleware
):
    """Логирует вход и выход
    обработки update."""

    __slots__ = (
        "log_state",
        "p_limit",
    )



    def __init__(
        self,
        log_state: bool = False,
        p_limit: int = 80,
    ) -> None:
        """Инициализируем настройки
        для логгирования."""

        super().__init__()

        if p_limit <= 0:
            raise ValueError(
                "p_limit must be "
                "greater than 0"
            )

        self.log_state = log_state
        self.p_limit = p_limit




    async def _state(self, data: EventData) -> str:
        """Безопасно извлекает текущее состояние
        пользователя (FSM) для лога."""

        if not self.log_state:
            return ""

        if isinstance(state := data.get("state"), FSMContext):
            with contextlib.suppress(Exception):
                if current := await state.get_state():
                    return f" | state={current}"
        return ""




    def _payload(self, event: TelegramObject | None) -> str:
        """Извлекает полезную нагрузку из
        события для записи в лог."""

        if isinstance(event, CallbackQuery):
            data = event.data or "empty"
            return f" | data={data[:self.p_limit]}"
        
        if isinstance(event, InlineQuery):
            query = event.query or "empty"
            return f" | query={query[:self.p_limit]}"
        
        return ""




    async def __call__(
        self,
        handler: Handler,
        event: TelegramObject,
        data: EventData,
    ) -> Any:
        """Перехватывает апдейт для записи
        подробного лога на входе и выходе.
        """

        if not isinstance(event, Update):
            return await handler(event, data)
        
        inner = event.event
        user = getattr(inner, "from_user", None)
        action = data.get("action_type", "unknown")
        u_id = user.id if user else "none"
        
        logger.debug(
            f"IN | update_id={event.update_id} | "
            f"type={action} | user_id={u_id} |"
            f"{await self._state(data)} |"
            f"{self._payload(inner)}"
        )

        return await handler(event, data)