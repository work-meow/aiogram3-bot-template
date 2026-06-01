from typing import Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from collections.abc import Awaitable, Callable


type EventData = dict[str, Any]
type Handler = Callable[
    [
        TelegramObject,
        EventData
    ],
    Awaitable[Any]
]



class ActionMiddleware(BaseMiddleware):
    """Универсальный парсер апдейтов. 1 раз
    вычисляет тип действия для всего пайплайна.
    """
    
    __slots__ = ()


    @staticmethod
    def _get_action(event: Update) -> str:
        """Моментально извлекает тип
        действия (Short-Circuit)."""
        
        # 1. СМС И КОМАНДЫ 
        # (Текст, Медиа и т.д.)
        if msg := event.message:
            text = msg.text or msg.caption
            if text and text.startswith("/"):
                cmd = text.split(maxsplit=1)[0][1:]
                return f"cmd_{cmd}"
            return f"msg_{msg.content_type}"
            
            
        # 2. НАЖАТИЯ ИНЛАЙН-КНОПОК
        if cb := event.callback_query:
            if data := cb.data:
                action = data.split(':', 1)[0]
                return f"cb_{action}"
            return "cb_empty"
            
            
        # 3. РЕДАКТИРОВАНИЕ 
        if event.edited_message:
            return "edited_msg"


        # 4. ИНЛАЙН-РЕЖИМ
        if event.inline_query:
            return "inline_query"
            
            
        # 5. СТАТУСЫ УЧАСТНИКОВ 
        if mem := event.my_chat_member:
            status = mem.new_chat_member.status
            return f"my_member_{status}"
            
        if mem := event.chat_member:
            status = mem.new_chat_member.status
            return f"member_{status}"


        # 6. ЗАЯВКИ НА ВСТУПЛЕНИЕ 
        # В ЗАКРЫТЫЙ КАНАЛ/ЧАТ
        if event.chat_join_request:
            return "join_request"


        # 7. ПЛАТЕЖИ (Telegram Stars)
        if event.pre_checkout_query:
            return "pre_checkout"
            
            
        if event.shipping_query:
            return "shipping"

        # 8. ОПРОСЫ
        if event.poll_answer:
            return "poll_answer"
            
        if event.poll:
            return "poll"

        # 9. ПОСТЫ В КАНАЛАХ 
        # (если бот добавлен в канал)
        if post := event.channel_post:
            return f"post_{post.content_type}"
            
        if event.edited_channel_post:
            return "edited_post"

        return "unknown"



    async def __call__(
        self,
        handler: Handler,
        event: TelegramObject,
        data: EventData,
    ) -> Any:
        """Перехватывает апдейт 
        на самом верхнем уровне."""
        
        # 1. Безопасная проверка типа 
        # и мгновенная запись в память
        data["action_type"] = (
            self._get_action(event) 
            if isinstance(event, Update) 
            else "unknown"
        )
            
        # 2. Передаем управление 
        # дальше по конвейеру (Zero I/O)
        return await handler(event, data)