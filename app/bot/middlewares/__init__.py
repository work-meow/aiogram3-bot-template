from aiogram import Dispatcher

from .logging import LoggingMiddleware
from .profiler import ProfilerMiddleware
from ..localization import setup_i18n


def setup_middlewares(dp: Dispatcher) -> None:
    """Регистрация всех middleware."""

    # 1. профилер обработки update.
    dp.update.outer_middleware(
        ProfilerMiddleware(
            slow_after=1.5,
            log_errors=True,
            log_fast=False,
        )
    )


    # 2. Локализация.
    setup_i18n().setup(dp)


    # 3. Логирование update.
    dp.update.middleware(
        LoggingMiddleware(
            log_state=True,
            p_limit=80,
        )
    )