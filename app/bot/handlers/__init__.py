from aiogram import Router

# Импортируем крупные узлы
from .common import common_router


def setup_routers() -> Router:
    """Главный сборщик маршрутов."""

    # Корневой роутер
    main_router = Router(name="main")

    # Собираем все ветки
    main_router.include_routers(
        # common_router,

    )

    return main_router