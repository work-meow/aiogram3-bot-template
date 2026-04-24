import os
import asyncio
import platform

from app.container import init_container
from app.scheduler import SchedulerManager
from app.logger import setup_logger, logger
from app.bot import init_bot, start_bot
from app.api import server_start



async def main() -> None:
    """Оркестратор запуска приложения."""

    # 1. Подготовка среды
    os.system("cls" if platform.system() == "Windows" else "clear")
    setup_logger()

    # 2. Инициализация DI контейнера
    container = await init_container()

    # 3. Сборка планировщика и бота
    bot, dp = await init_bot(container)
    scheduler = SchedulerManager(container)

    try:
        # Внешний блок ловит ошибки инициализации и общие сбои
        logger.info("🚀 Запуск параллельных сервисов...")
        await scheduler.start()

        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(server_start(container))
                tg.create_task(start_bot(bot, dp))

        except* Exception as eg:
            # Ловим ошибки из параллельных задач
            logger.opt(exception=eg).error("Критический сбой в TaskGroup")

    except Exception as e:
        # Ловим ошибки, случившиеся вне TaskGroup
        logger.opt(exception=True).error(f"Ошибка окружения или запуска: {e}")
        raise

    finally:
        await scheduler.stop()
        await container.close()



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 Работа завершена пользователем")