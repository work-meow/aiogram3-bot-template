from typing import Literal
from aiogram.filters import Filter
from aiogram.types import Message


AlbumType = Literal[
    "photo", 
    "video", 
    "document",
    "audio"
]


class AlbumContains(Filter):
    """Кастомный фильтр для определения 
    типа контента в медиагруппе."""
    
    __slots__ = ("m_type",)


    def __init__(self, m_type: AlbumType) -> None:
        self.m_type = m_type


    async def __call__(
        self, 
        message: Message, 
        album: list[Message]
    ) -> bool:
        """Проверяет содержимое альбома.
        Аргумент 'album' автоматически
        инжектится из нашей мидлвари."""
        
        if not album:
            return False
            
        return bool(getattr(
            album[0], 
            self.m_type,
            None
        ))