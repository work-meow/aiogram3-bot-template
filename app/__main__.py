import os
import asyncio
import platform

from contextlib import AsyncExitStack
from app.container import init_container
from app.api import create_app, run_server
from app.bot import bot_lifespan, get_tg_webhook
from app.logger import logger, setup_logger
from app.scheduler import SchedulerManager
from app.bot import init_bot, start_bot
from app.settings import Settings




# Ускорение asyncio через uvloop 
# (на Windows fallback на стандартный).
try:
    import uvloop
    uvloop.install()
except ImportError:
    pass





async def main() -> None:
    """Оркестратор запуска
    всего приложения."""

    # 1. Подготовка 
    # среды к запуску
    os.system("cls" if platform.system() == "Windows" else "clear")
    setup_logger()


    # 2. Инициализация 
    # зависимостей через DI контейнер
    container = await init_container()
    bot, dispatcher = await init_bot(container)
    settings = await container.get(Settings)
    scheduler = SchedulerManager(container)
    api_app = create_app(container)


    # 3. Конфигурация 
    # режима работы бота
    if settings.BOT_MODE == "webhook":
        api_app.include_router(
            get_tg_webhook(
                bot=bot, dp=dispatcher, 
                settings=settings
            )
        )

    try:
        # 4. Старт фоновых 
        # процессов и основного цикла
        logger.info("🚀 Запуск сервисов...")
        await scheduler.start()

        try:
            # Жизненный цикл вебхука 
            # (авто-установка/удаление)
            async with AsyncExitStack() as stack:
                if settings.BOT_MODE == "webhook":
                    await stack.enter_async_context(
                        bot_lifespan(bot, dispatcher, settings)
                    )

                # Безопасный параллельный запуск 
                # (упадет одна задача — отменятся все)
                async with asyncio.TaskGroup() as tg:
                    server_task = tg.create_task(
                        run_server(api_app, settings)
                    )
                    
                    if settings.BOT_MODE == "polling":
                        polling_task = tg.create_task(
                            start_bot(bot, dispatcher)
                        )
                        
                        server_task.add_done_callback(
                            lambda _: polling_task.cancel(
                                msg="Uvicorn shutdown"
                            )
                        )

        # Перехват сбоев 
        # внутри параллельных задач
        except* Exception as eg:
            logger.opt(exception=eg).error(
                "Критический сбой "
                "в TaskGroup"
            )
            raise
        
    # Перехват ошибок до 
    # TaskGroup или внутри стека
    except Exception as e:
        logger.opt(exception=True).error(
            "Ошибка среды окружения "
            f"или запуска: {e}"
        )
        raise

    finally:
        await scheduler.stop()
        await container.close()




if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 Работа завершена юзером")