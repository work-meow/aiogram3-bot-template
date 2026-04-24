import contextlib

from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.exceptions import TelegramAPIError
from aiogram.types import TelegramObject, User
from dishka.integrations.aiogram import FromDishka, inject

from app.settings import Settings


class IsSubscribed(BaseFilter):
    """Проверка подписки на канал."""

    @inject
    async def __call__(
        self,
        event: TelegramObject,
        bot: FromDishka[Bot],
        settings: FromDishka[Settings]
    ) -> bool:

        # 1. Получаем юзера из евента
        user: User | None = getattr(event, "from_user", None)
        if not user:
            return False

        # 2. Выход, если канал не задан
        if not settings.CHANNEL_ID:
            return True

        # 3. Запрос к API с подавлением ошибок
        with contextlib.suppress(TelegramAPIError):
            member = await bot.get_chat_member(
                chat_id=settings.CHANNEL_ID,
                user_id=user.id
            )

            # 4. Проверка статуса
            return member.status not in (
                "left", "kicked", "banned"
            )

        return False