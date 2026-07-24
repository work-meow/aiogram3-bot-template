from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject, Message


class ThreadFilter(BaseFilter):
    """Ограничивает работу роутера
    сообщениями из топиков/тредов."""

    def __init__(self, *thread_ids: int) -> None:
        self.thread_ids = frozenset(thread_ids)


    async def __call__(self, event: TelegramObject) -> bool:
        if msg := (
            event 
            if isinstance(event, Message) 
            else getattr(event, "message", None)
        ):
            return (
                msg.message_thread_id in self.thread_ids 
                if self.thread_ids else bool(msg.is_topic_message)
            )
        return False
