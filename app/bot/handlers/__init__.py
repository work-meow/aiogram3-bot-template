from aiogram import Router

from .example import example_router


def setup_routers() -> Router:
    """Главный сборщик
    маршрутов."""

    main_router = Router(name="main")
    main_router.include_routers(example_router)
    return main_router