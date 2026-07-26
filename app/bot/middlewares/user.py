from typing import Any
from loguru import logger
from aiogram import BaseMiddleware
from collections.abc import Awaitable, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import TelegramObject

from app.storage.models import User



type EventData = dict[str, Any]
type Handler = Callable[
    [
        TelegramObject,
        EventData
    ],
    Awaitable[Any]
]



class UserMiddleware(BaseMiddleware):
    """Получает/создаёт пользователя
    и пробрасывает его в дальше."""

    async def __call__(
        self,
        handler: Handler,
        event: TelegramObject,
        data: EventData,
    ) -> Any:
        """Перехватывает event, достаёт 
        юзера и кладёт в data."""

        tg_user = data.get("event_from_user")
        if not tg_user:
            return await handler(event, data)

        container = data.get("dishka_container")
        if not container:
            raise RuntimeError(
                "UserMiddleware: dishka"
                "не найден в data"
            )

        session = await container.get(AsyncSession)
        user, created = await User.get_or_create(session, tg_user)
        if created:
            logger.info(f"👋 New user: tg_id={tg_user.id}")
        await session.commit()
        
        data["user"] = user
        return await handler(event, data)
