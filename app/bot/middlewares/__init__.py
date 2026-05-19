from aiogram import Dispatcher
from .user import UserMiddleware
from .logging import LoggingMiddleware
from .profiler import ProfilerMiddleware
from ..localization import setup_i18n


def setup_middlewares(dp: Dispatcher) -> None:
    """Регистрация всех middleware."""

    # 1. Профилер обр. upd
    dp.update.outer_middleware(
        ProfilerMiddleware(
            slow_after=1.5,
            log_errors=True,
            log_fast=True,
        )
    )
    
    # 2. Берем юзера из БД 
    # на уровне ВСЕГО апдейта.
    dp.update.outer_middleware(
        UserMiddleware()
    )

    # 3. Локализация
    setup_i18n().setup(dp)

    # 4. Логирование upd
    dp.update.middleware(
        LoggingMiddleware(
            log_state=True,
            p_limit=80,
        )
    )