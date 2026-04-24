# fmt: off
# isort: off
import time
import asyncio

from loguru import logger
from typing import Any, Dict, Callable, Awaitable

from .objects import MemoryRequest, RequestStatus


class QueueManager:
    """Менеджер очереди запросов в памяти."""

    def __init__(self, workers: int = 50):
        self.running = False
        self.workers = workers
        self.queue = asyncio.Queue(20000)
        self._stop_event = asyncio.Event()
        logger.info(f"MemoryQueueManager: {workers} workers")


    def stop(self):
        """Внешний метод для инициации мягкой остановки."""
        self._stop_event.set()



    async def _shutdown(self) -> None:
        """Внутренний метод: раскидываем таблетки воркерам."""
        logger.info("Начинаем остановку воркеров (Poison Pill)...")
        for _ in range(self.workers):
            await self.queue.put(None)



    async def _process(self, req: MemoryRequest, handler: Callable, wid: int) -> None:
        """Обрабатывает один запрос."""
        logger.debug(f"[W{wid}] {req.id}")
        try:
            req.status = RequestStatus.PROCESSING

            if await handler(req):
                req.status = RequestStatus.COMPLETED
                req.processed_at = time.monotonic()

            else:
                req.status = RequestStatus.FAILED
                req.processed_at = time.monotonic()
                req.error = "Handler returned False"

        except Exception as e:
            logger.exception(f"[W{wid}] Ошибка {req.id}: {e}")
            req.processed_at = time.monotonic()
            req.status = RequestStatus.FAILED
            req.error = str(e)

        finally:
            req.done_event.set()



    async def _worker(self, wid: int, handler: Callable[[MemoryRequest], Awaitable[bool]]) -> None:
        """Воркер для обработки запросов."""
        while True:
            try:
                req = await self.queue.get()

                # Проверяем, "отравленную таблетку"
                if req is None:
                    self.queue.task_done()
                    logger.debug(f"[W{wid}] Получил сигнал завершения, выхожу.")
                    break

                # Обычная обработка запроса
                await self._process(req, handler, wid)
                self.queue.task_done()

            except Exception as e:
                logger.exception(f"Ошибка в цикле воркера W{wid}: {e}")
                await asyncio.sleep(0.1)



    async def process_queue(self, handler: Callable[[MemoryRequest], Awaitable[bool]]) -> None:
        """Запускает обработку очереди."""
        logger.info(f"Запуск {self.workers} воркеров")
        self.running = True
        self._stop_event.clear()

        try:
            async with asyncio.TaskGroup() as tg:
                for i in range(self.workers):
                    tg.create_task(self._worker(i, handler))

                # Ждем сигнала остановки
                await self._stop_event.wait()
                await self._shutdown()

        except asyncio.CancelledError:
            logger.info("Остановка process_queue (CancelledError).")
            raise

        except Exception as e:
            logger.exception(f"Ошибка очереди: {e}")

        finally:
            self.running = False
            logger.info("Очередь полностью остановлена.")



    async def enqueue(self, payload: Dict[str, Any]) -> MemoryRequest:
        """Добавляет запрос в очередь."""
        req = MemoryRequest(payload=payload)
        await self.queue.put(req)
        logger.debug(f"Добавлен запрос {req.id}")
        return req
