from typing import Any
from loguru import logger
from dishka import AsyncContainer
from abc import ABC, abstractmethod
from apscheduler.triggers.base import BaseTrigger


class BaseJob(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def get_trigger(self, is_dev: bool) -> BaseTrigger:
        ...

    @abstractmethod
    async def run(self, container: AsyncContainer, **kwargs: Any) -> None:
        ...

    async def __call__(self, **kwargs: Any) -> None:
        logger.info(f"⏳ Старт задачи: {self.name}")

        from app.scheduler import get_container
        try:
            async with get_container()() as request_container:
                await self.run(request_container, **kwargs)

            logger.success(f"🏁 Задача {self.name} успешно завершена")
        except Exception as e:
            logger.opt(exception=True).error(f"💥 Ошибка в задаче {self.name}: {e}")