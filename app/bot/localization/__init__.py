from typing import Any
from pathlib import Path
from loguru import logger
from aiogram.types import User
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.managers import BaseManager
from aiogram_i18n.cores import FluentCompileCore

from . import formatters as f


LOCALES_DIR = Path(__file__).parent.resolve() / "locales"


class LocaleManager(BaseManager):
    """Менеджер для работы с локалями."""

    async def startup(self, *args: Any, **kwargs: Any) -> None:
        """Срабатывает при запуске диспетчера."""
        logger.info("🌍 LocaleManager: запущен")

    async def shutdown(self, *args: Any, **kwargs: Any) -> None:
        """Срабатывает при остановке диспетчера."""
        logger.info("🌍 LocaleManager: остановлен")

    async def get_locale(self, **kwargs: Any) -> str:
        user: User | None = kwargs.get("event_from_user")

        # 1. TODO: Получение из БД

        # 2. Системный язык Telegram
        if user and user.language_code:
            return user.language_code

        # 3. Безопасный фоллбэк
        return self.default_locale or "ru"

    async def set_locale(self, locale: str, **kwargs: Any) -> None:
        """TODO: Сохранение языка в БД."""
        pass



def setup_i18n() -> I18nMiddleware:
    """Сборка движка локализации."""
    locale_path = LOCALES_DIR / "{locale}"

    # 1. Собираем ядро
    core = FluentCompileCore(
        path=locale_path,
        default_locale="ru",
        use_isolating=False,
        raise_key_error=False,
        functions={
            # Строки и числа
            "UP": str.upper,
            "LOW": str.lower,
            "TRUNC": f.trunc,
            "TIME": f.fmt_time,
            "CAP": str.capitalize,
            "MONEY": f.fmt_money,
            "DATE": f.fmt_date,
            "PHONE": f.phone,
            "NUM": f.fmt_num,
            "DT": f.fmt_dt,
            "PCT": f.pct,

            # HTML теги
            "B": f.bold,
            "PRE": f.pre,
            "I": f.italic,
            "S": f.strike,
            "CODE": f.code,
            "LINK": f.link,
            "U": f.underline,
            "QUOTE": f.quote,
            "SPOIL": f.spoiler,
            "MENTION": f.mention,
        }
    )

    # 2. Оборачиваем в мидлварь
    middleware = I18nMiddleware(
        core=core,
        manager=LocaleManager(
            default_locale="ru"
        )
    )

    logger.info("🌍 I18n ready!")
    return middleware
