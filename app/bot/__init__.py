from typing import Any
from loguru import logger
from dishka import AsyncContainer
from aiogram import Bot, Dispatcher
from aiogram.types import TelegramObject
from collections.abc import Callable, Awaitable
from aiogram.fsm.storage.memory import MemoryStorage
from dishka.integrations.aiogram import (
    ContainerMiddleware as DishkaMW,
    setup_dishka
)

from app.bot.events import on_error, on_shutdown, on_startup
from app.bot.middlewares import setup_middlewares
from app.bot.handlers import setup_routers


type EventData = dict[str, Any]
type Handler = Callable[
    [
        TelegramObject,
        EventData
    ],
    Awaitable[Any]
]


def _dishka_patch() -> None:
    """Выполняется ЕДИНОЖДЫ. Подменяет 
    логику мидлвари, чтобы на весь апдейт 
    открывалась строго одна сессия 
    БД (REQUEST-скоуп)."""

    async def _upd_call(
        self: DishkaMW,
        handler: Handler,
        event: TelegramObject,
        data: EventData,
        _orig=DishkaMW.__call__
    ) -> Any:
        """Вызывается ПОСТОЯННО на 
        каждое событие от Telegram."""
        
        if "_dishka_handled" in data:
            return await handler(event, data)
            
        data["_dishka_handled"] = True
        return await _orig(self, handler, event, data)

    DishkaMW.__call__ = _upd_call


_dishka_patch()



async def init_bot(
    container: AsyncContainer
) -> tuple[Bot, Dispatcher]:
    """Сборка бота, диспетчера и 
    настройка экосистемы."""
    
    #  Инициализация бота
    bot = await container.get(Bot)
    dp = Dispatcher(storage=MemoryStorage())

    # 2 Прокидываем APP-контейнер
    dp["dishka_container"] = container
    setup_dishka(container, dp, auto_inject=True)

    # 2. Регистрация жизненного цикла
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.errors.register(on_error)

    # 3. Подключаем мидлвари
    setup_middlewares(dp)                          
    
    # 4. Подключаем роутеры
    dp.include_router(setup_routers())             

    logger.info("🤖 Bot is ready!")
    return bot, dp



async def start_bot(bot: Bot, dp: Dispatcher) -> None:
    """Запуск поллинга бота."""
    
    # 1. Получаем пропущенные апдейты
    await bot.delete_webhook(False)

    # 2. Слушаем исключительно те события, 
    # на которые зарегистрированы хендлеры
    used_upd = dp.resolve_used_update_types()
    await dp.start_polling(bot, allowed_updates=used_upd)
    