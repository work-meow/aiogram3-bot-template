import time

from typing import Any
from loguru import logger
from aiogram import BaseMiddleware
from collections.abc import Awaitable, Callable
from aiogram.types import TelegramObject, Update


Handler = Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]]

class ProfilerMiddleware(BaseMiddleware):
    """Замер скорости выполнения."""

    def __init__(self, slow: float = 1.0) -> None:
        self.slow = slow
        super().__init__()


    async def __call__(
        self,
        handler: Handler,
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:

        # 1. Только корневой Update
        if not isinstance(event, Update):
            return await handler(event, data)

        # 2. Получаем метаданные
        uid: int = event.update_id
        t0 = time.perf_counter()

        try:
            # 3. Передача управления дальше
            return await handler(event, data)

        finally:
            dt = time.perf_counter() - t0
            if dt >= self.slow:
                logger.warning(f"🐢 SLOW | Upd: {uid} | {dt:.3f}s")
            else: logger.debug(f"⏱ TIME | Upd: {uid} | {dt:.3f}s")