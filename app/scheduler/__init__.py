from loguru import logger
from typing import Sequence
from dishka import AsyncContainer
from sqlalchemy import create_engine
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from app.settings import get_settings
from .jobs import JOBS, BaseJob



_di_container: AsyncContainer | None = None

def get_container() -> AsyncContainer:
    """Ленивый доступ к DI-контейнеру изнутри задач."""
    if not _di_container:
        raise RuntimeError("DI-контейнер is None")
    return _di_container



class SchedulerManager:
    def __init__(self, container: AsyncContainer, jobs: Sequence[BaseJob] | None = None):
        if container is None:
            raise ValueError("DI-контейнер is None")

        global _di_container
        _di_container = container

        # 1. Среда выполнения
        self._is_dev = get_settings().APP_ENV == "dev"

        # 2. Используем psycopg
        url = get_settings().DATABASE_URL
        sync_url = url.replace("+asyncpg", "+psycopg")

        # 3. Изолированный пул соединений
        self._engine = create_engine(
            sync_url,
            pool_size=2,
            max_overflow=3,
            pool_pre_ping=True,
            pool_recycle=1800
        )

        # 3. Конфигурация движка
        self._scheduler = AsyncIOScheduler(
            executors={"default": AsyncIOExecutor()},
            jobstores={"default": SQLAlchemyJobStore(
                engine=self._engine,
                tablename="sys_scheduler_jobs"
            )},
            job_defaults={
                "coalesce": True,
                "misfire_grace_time": 86400,
                "max_instances": 1
            },
            timezone="UTC"
        )

        # 4. Добавляем задачи
        for job in (jobs or JOBS):
            self.register(job)



    def register(self, job: BaseJob) -> None:
        """Обновление или добавление задачи в БД."""
        self._scheduler.add_job(
            id=job.name,
            func=job.__call__,
            trigger=job.get_trigger(self._is_dev),
            replace_existing=True
        )
        logger.debug(f"📌 Запланировано: {job.name}")



    async def start(self) -> None:
        """Запуск планировщика задач."""
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("🟢 Планировщик запущен")



    async def stop(self) -> None:
        """Остановка планировщика задач."""
        if self._scheduler.running:
            self._scheduler.shutdown(wait=True)

        self._engine.dispose()
        logger.info("🛑 Планировщик остановлен")
