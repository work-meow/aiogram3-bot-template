from typing import Any
from loguru import logger
from dishka import AsyncContainer
from aiogram import Bot, Dispatcher
from aiogram.types import TelegramObject
from collections.abc import Callable, Awaitable
from aiogram.fsm.storage.memory import MemoryStorage
from dishka.integrations.aiogram import (
    ContainerMiddleware as DishkaMW, 
    setup_dishka as setup_deps
)

from app.bot.webhook import get_tg_webhook, bot_lifespan
from app.bot.middlewares import setup_middlewares
from app.bot.handlers import setup_routers
from app.bot.events import setup_events



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
    setup_deps(container, dp, auto_inject=True)

    # 2. Эвенты
    setup_events(dp)

    # 3. Мидлвари
    setup_middlewares(dp)                          
    
    # 4. Роутеры и обработчики
    dp.include_router(setup_routers())    
             
    logger.info("🤖 Bot is ready!")
    return bot, dp




async def start_bot(
    bot: Bot, 
    dp: Dispatcher
) -> None:
    """Запуск бота
    поллинга."""
    
    # 1. Сохраняем 
    # пропущенные апдейты
    await bot.delete_webhook(False)

    # 2. Слушаем исключительно те события,
    # на которые зарегистрированы хендлеры
    used_upd = dp.resolve_used_update_types()
    await dp.start_polling(bot,
        allowed_updates=used_upd,
        handle_signals=False,
        polling_timeout=50
    )
    