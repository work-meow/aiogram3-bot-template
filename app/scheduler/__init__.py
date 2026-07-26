import asyncio

from loguru import logger
from typing import Sequence
from dishka import AsyncContainer
from sqlalchemy import create_engine
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from app.settings import get_settings
from .jobs import JOBS, BaseJob




# Реестр задач и
# главный event loop с di.
_registry: dict[str, BaseJob] = {}
_loop: asyncio.AbstractEventLoop | None = None
_di_container: AsyncContainer | None = None



def get_container() -> AsyncContainer:
    """Ленивый доступ к DI изнутри."""
    if not _di_container:
        raise RuntimeError("DI-контейнер is None")
    return _di_container



def run_job(name: str) -> None:
    """Точка входа для APScheduler. Синхронная и
    сериализуемая: крутится в потоке планировщика,
    а корутину отдаёт в главный event loop."""

    if (job := _registry.get(name)) is None:
        logger.warning(f"⚠️ Задача {name} не найдена в коде")
        return

    if _loop is None or _loop.is_closed():
        logger.error(f"❌ Event loop недоступен, пропуск {name}")
        return

    asyncio.run_coroutine_threadsafe(job(), _loop).result()




class SchedulerManager:
    def __init__(
        self,
        container: AsyncContainer,
        jobs: Sequence[BaseJob] | None = None
    ):
        if container is None:
            raise ValueError("DI-контейнер is None")

        global _di_container
        _di_container = container
        self._is_dev = get_settings().APP_ENV == "dev"
        self._jobs = tuple(jobs or JOBS)

        _registry.clear()
        _registry.update({
            j.name: j for j
            in self._jobs
        })

        url = get_settings().DATABASE_URL
        sync_url = url.replace("+asyncpg", "+psycopg")
        self._engine = create_engine(
            sync_url,
            pool_size=2,
            max_overflow=3,
            pool_pre_ping=True,
            pool_recycle=1800
        )

        self._scheduler = BackgroundScheduler(
            jobstores={"default": SQLAlchemyJobStore(
                engine=self._engine,
                tablename="scheduler_jobs"
            )},
            job_defaults={
                "coalesce": True,
                "misfire_grace_time": 86400,
                "max_instances": 1
            },
            timezone="UTC"
        )



    def register(self, job: BaseJob) -> None:
        """Синхронизация задачи с хранилищем. У существующей
        НЕ трогаем next_run_time, иначе пропущенный за
        простой запуск потеряется вместо догона."""

        _registry[job.name] = job
        trigger = job.get_trigger(self._is_dev)

        if (old := self._scheduler.get_job(job.name)) is None:
            self._scheduler.add_job(
                id=job.name,
                func=run_job,
                args=(job.name,),
                trigger=trigger
            )
            logger.debug(f"📌 Запланировано: {job.name}")
            return

        if str(old.trigger) != str(trigger):
            self._scheduler.reschedule_job(job.name, trigger=trigger)
            logger.info(f"🔁 Расписание обновлено: {job.name}")
            return

        logger.debug(
            f"📌 Восстановлено: {job.name} "
            f"-> {old.next_run_time}"
        )



    def _drop_orphans(self) -> None:
        """Удаляет из БД задачи,
        которых нет в коде."""

        for stored in self._scheduler.get_jobs():
            if stored.id not in _registry:
                self._scheduler.remove_job(stored.id)
                logger.warning(f"🗑 Удалена устаревшая: {stored.id}")



    async def start(self) -> None:
        """Запуск планировщика задач."""

        if self._scheduler.running:
            return

        global _loop
        _loop = asyncio.get_running_loop()
        self._scheduler.start(paused=True)

        for job in self._jobs:
            self.register(job)

        self._drop_orphans()
        self._scheduler.resume()
        logger.info("🟢 Планировщик запущен")



    async def stop(self) -> None:
        """Остановка планировщика задач."""

        if self._scheduler.running:
            await asyncio.to_thread(
                self._scheduler.shutdown,
                wait=True
            )

        self._engine.dispose()
        logger.info("🛑 Планировщик остановлен")
