# fmt: off
# isort: off
from loguru import logger
from typing import Any, Dict, Callable, Awaitable

from .manager import QueueManager
from .objects import *


class QueueService:
    """Фасад сервиса очереди."""

    def __init__(self, manager: QueueManager):
        """Инициализация сервиса очереди."""
        self._manager = manager
        logger.info("🚀 QueueService создан")


    async def add_request(self, payload: Dict[str, Any]) -> MemoryRequest:
        """Добавляет запрос в очередь."""
        return await self._manager.enqueue(payload)


    async def start_processing(self, handler: Callable[[MemoryRequest], Awaitable[bool]]) -> None:
        """Запускает обработку очереди."""
        await self._manager.process_queue(handler)


    def stop(self) -> None:
        """Остановка очереди."""
        self._manager.stop()
