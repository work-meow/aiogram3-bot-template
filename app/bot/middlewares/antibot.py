from typing import Any
from loguru import logger
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from collections.abc import Awaitable, Callable


type EventData = dict[str, Any]
type Handler = Callable[
    [
        TelegramObject,
        EventData
    ],
    Awaitable[Any]
]


class AntiBotMiddleware(BaseMiddleware):
    """Блокирует апдейты от ботов 
    на самом раннем этапе."""

    __slots__ = ()
    
    async def __call__(
        self,
        handler: Handler,
        event: TelegramObject,
        data: EventData,
    ) -> Any:
        """Блокирует апдейты от ботов 
        на самом раннем этапе."""
    
        tg_user: User | None = data.get("event_from_user")
        if tg_user and tg_user.is_bot:
            logger.info(
                f"🤖 Blocked bot: id={tg_user.id} "
                f"username={tg_user.username}"
            )
            return None
        
        return await handler(event, data)