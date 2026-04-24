from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject, Message, CallbackQuery


class ChatTypeFilter(BaseFilter):
    """Ограничивает работу роутера конкретными
    типами чатов (private, group, supergroup)."""


    def __init__(self, chat_types: str | list[str]) -> None:
        if isinstance(chat_types, str):
            chat_types = [chat_types]
        self.chat_types: set[str] = set(chat_types)


    async def __call__(self, event: TelegramObject) -> bool:
        if isinstance(event, Message):
            return event.chat.type in self.chat_types

        if isinstance(event, CallbackQuery) and event.message:
            return event.message.chat.type in self.chat_types

        return False