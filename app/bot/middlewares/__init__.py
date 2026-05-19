from aiogram import Dispatcher, BaseMiddleware

from .user import UserMiddleware
from .logging import LoggingMiddleware
from .profiler import ProfilerMiddleware
from ..localization import setup_i18n



def _bind(
    dp: Dispatcher, 
    mw: BaseMiddleware, 
    skip: set[str] = frozenset({
        "update",
    })
) -> None:
    """Вешает middleware на все 
    observer'ы dp, кроме skip."""
    
    for name, obs in dp.observers.items():
        if name not in skip:
            obs.middleware(mw)



def setup_middlewares (dp: Dispatcher) -> None:
    """Регистрация всех middleware."""

    # 1. Профилер обр. update
    dp.update.outer_middleware(
        ProfilerMiddleware(
            slow_after=1.5,
            log_errors=True,
            log_fast=True,
        )
    )
    
    # 2. Локализация
    setup_i18n().setup(dp)

    # 3. Логирование update
    dp.update.middleware(
        LoggingMiddleware(
            log_state=True,
            p_limit=80,
        )
    )

    # 4. Получаем юзера
    # из бд (REQUEST scope)
    _bind(dp, UserMiddleware())