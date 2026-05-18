from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject


class EnvFilter(BaseFilter):
    """Пропускает апдейты  
    только для определенного 
    окружения."""

    def __init__(self, got: str, want: str) -> None:
        self.is_match = got == want

    async def __call__(self, event: TelegramObject) -> bool:
        return self.is_match