from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject, Message, CallbackQuery


class ChatTypeFilter(BaseFilter):
    """Ограничивает работу роутера конкретными
    типами чатов (private, group, supergroup)."""
    
    def __init__(self, *chat_types: str) -> None:
        self.chat_types = set(chat_types)

    async def __call__(self, event: TelegramObject) -> bool:
        if msg := (event if isinstance(event, Message) else getattr(event, "message", None)):
            return msg.chat.type in self.chat_types
        return False