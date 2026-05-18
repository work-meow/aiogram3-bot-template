from aiogram import Router

from .common import common_router


def setup_routers() -> Router:
    """Главный сборщик
    маршрутов."""

    main_router = Router(name="main")
    main_router.include_routers(common_router)
    return main_router