from aiogram import Dispatcher

from .user import UserMiddleware
from .action import ActionMiddleware
from .antibot import AntiBotMiddleware
from .logging  import LoggingMiddleware
from .profiler  import ProfilerMiddleware
from .mediagroup import MediaGroupMiddleware
from .statistic import MetricsMiddleware
from ..localization import setup_i18n


def setup_middlewares(dp: Dispatcher) -> None:
    """Регистрация всех middleware 
    в строгом порядке."""

    # 1. Мгновенно отсекаем 
    # доступ ботам (Zero I/O)
    dp.update.outer_middleware(
        AntiBotMiddleware()
    )
    
    # 2. Парсим тип действия 
    # один раз для всех (Zero I/O)
    dp.update.outer_middleware(
        ActionMiddleware()
    )
    
    # 3. Агрегируем альбомами 
    # и глушим дубликаты (Zero I/O)
    dp.update.outer_middleware(
        MediaGroupMiddleware(
            latency=0.5
        )
    )
    
    # 4. Собираем метрики 
    # в Prometheus (Zero I/O)
    dp.update.outer_middleware(
        MetricsMiddleware()
    )

    # 5. Запускаем профилер 
    # и гистограмму (Zero I/O)
    dp.update.outer_middleware(
        ProfilerMiddleware(
            slow_after=1.5,
            log_errors=True,
            log_fast=True,
        )
    )

    # 6. Берем юзера из БД 
    # на уровне !ВСЕГО! апдейта.
    dp.update.outer_middleware(
        UserMiddleware()
    )

    # 7. Локализация 
    # для пользователей
    setup_i18n().setup(dp)

    # 8. Логируем fsm
    # вход/выход события
    # (enabled=True для отладки)
    dp.update.middleware(
        LoggingMiddleware(
            enabled=False,
            log_state=True,
            p_limit=80,
        )
    )
    