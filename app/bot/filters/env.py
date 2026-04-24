from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from dishka.integrations.aiogram import FromDishka, inject

from app.settings import Settings


class EnvFilter(BaseFilter):
    """Пропускает апдейты только если
    текущее окружение совпадает с целевым."""

    def __init__(self, target_env: str) -> None:
        self.target_env = target_env

    @inject
    async def __call__(
        self,
        event: TelegramObject,
        settings: FromDishka[Settings]
    ) -> bool:

        return settings.APP_ENV == self.target_env