from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from aiogram.exceptions import TelegramAPIError


class IsSubscribed(BaseFilter):
    """Проверка подписки пользователя на канал.
    Пропускает апдейт дальше, только если юзер
    является участником канала."""

    __slots__ = ("channel_id",)
    _UNSUBSCRIBED = frozenset({"left", "kicked", "banned"})


    def __init__(self, channel_id: int | str | None) -> None:
        self.channel_id = channel_id


    async def __call__(self, event: TelegramObject, bot: Bot) -> bool:
        if not self.channel_id:
            return True

        if not (user := getattr(event, "from_user", None)):
            return False

        try:
            member = await bot.get_chat_member(
                chat_id=self.channel_id,
                user_id=user.id
            )
            return member.status not in self._UNSUBSCRIBED

        except TelegramAPIError:
            return False