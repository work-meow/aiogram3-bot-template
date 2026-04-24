from loguru import logger
from dishka import AsyncContainer
from aiogram import Bot, Dispatcher
from dishka.integrations.aiogram import setup_dishka
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.events import on_shutdown, on_startup, on_error
from app.bot.middlewares import setup_middlewares
from app.bot.handlers import setup_routers


async def init_bot(container: AsyncContainer) -> tuple[Bot, Dispatcher]:
    """Инициализация Bot и Dispatcher."""

    # 1. Получаем бота
    bot = await container.get(Bot)

    # 2. Собираем диспетчер
    dp = Dispatcher(storage=MemoryStorage())

    # 3. Прокидываем DI в контекст
    dp["dishka_container"] = container

    # 4. Регистрация событий
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.errors.register(on_error)

    # 5. Подключаем мидллвари
    setup_middlewares(dp)

    # 6. Регистрация роутеров
    dp.include_router(setup_routers())

    # 7. Связываем с DI-контейнером
    setup_dishka(container, dp, auto_inject=True)

    logger.info("🤖 Бот инициализирован")
    return bot, dp



async def start_bot(bot: Bot, dp: Dispatcher) -> None:
    """Старт поллинга бота."""

    # 1. Обрабатываем пропущенные апдейты
    await bot.delete_webhook(drop_pending_updates=False)

    # 2. Слушаем события, для которых есть хендлеры
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())