import asyncio

from typing import Any
from aiogram import BaseMiddleware
from collections.abc import Awaitable, Callable
from aiogram.types import (
    TelegramObject,
    Message,
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



class MediaGroupMiddleware(BaseMiddleware):
    """Агрегирует элементы медиагруппы 
    (альбома) в единый пайплайн."""
    
    __slots__ = (
        "latency", 
        "cache"
    )


    def __init__(
        self, 
        latency: float = 0.3
    ) -> None:
        """Инициализируем настройки
        агрегации медиагруппы."""
        
        super().__init__()
        self.latency = latency
        self.cache: dict[str, list[Message]] = {}


    async def __call__(
        self,
        handler: Handler,
        event: TelegramObject,
        data: EventData,
    ) -> Any:
        """Группирует медиа и пропускает 
        дальше только один запрос."""
        
        if not isinstance(event, Update):
            return await handler(event, data)

        # 1. Пропускаем одиночные сообщения
        msg = event.message or event.channel_post
        if not msg or not msg.media_group_id:
            return await handler(event, data)

        # 2. Если альбом собирается, 
        # добавляем файл и глушим апдейт
        group_id = msg.media_group_id
        if group_id in self.cache:
            self.cache[group_id].append(msg)
            return

        try:
            # 3. Даем Telegram 
            # дослать остальные части
            self.cache[group_id] = [msg]
            await asyncio.sleep(self.latency)
            
        finally:
            # 4. Очищаем память СРАЗУ.
            # до запуска долгих хендлеров.
            album_msgs = self.cache.pop(group_id, [])
            
        if album_msgs:
            # 5. Сортируем, сохраняя исходный порядок файлов
            album = sorted(album_msgs, key=lambda x: x.message_id)
            
            # 6. Переопределяем тип и 
            # передаем количество файлов
            data["action_type"] = "msg_album"
            data["items_count"] = len(album)
            data["album"] = album
            
            # 7. Пускаем собранный 
            # список дальше по цепочке
            return await handler(event, data)