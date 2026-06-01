from typing import Any
from loguru import logger
from time import perf_counter
from aiogram import BaseMiddleware
from collections.abc import Awaitable, Callable
from aiogram.types import TelegramObject, Update

from app.metrics import DURATION


type EventData = dict[str, Any]
type Handler = Callable[
    [
        TelegramObject,
        EventData
    ],
    Awaitable[Any]
]



class ProfilerMiddleware(
    BaseMiddleware
):
    """Профилирует время
    обработки update."""

    __slots__ = (
        "slow_after",
        "log_errors",
        "log_fast",
    )



    def __init__(
        self,
        slow_after: float = 1.5,
        log_errors: bool = True,
        log_fast: bool = False,
    ) -> None:
        """Инициализируем настройки
        для профилирования."""

        super().__init__()

        if slow_after <= 0:
            raise ValueError(
                "Slow_after must be "
                "greater than 0"
            )

        self.slow_after = float(slow_after)
        self.log_errors = log_errors
        self.log_fast = log_fast


                

    def _log(
        self,
        action: str,
        upd_id: int,
        elapsed: float,
        error: Exception | None,
    ) -> None:
        """Записывает информацию об
        обработке апдейта в логи."""
        
        DURATION.labels(
            service="bot", 
            action_type=action
        ).observe(elapsed)

        if error is not None and self.log_errors:
            logger.opt(exception=error).error(
                f"UPDATE ERROR | update_id={upd_id} | "
                f"type={action} | elapsed={elapsed:.3f}s"
            )
            return

        if elapsed >= self.slow_after:
            logger.warning(
                f"SLOW UPDATE | update_id={upd_id} | "
                f"type={action} | elapsed={elapsed:.3f}s"
            )
            return

        if self.log_fast:
            logger.debug(
                f"UPDATE TIME | update_id={upd_id} | "
                f"type={action} | elapsed={elapsed:.3f}s"
            )
            return




    async def __call__(
        self,
        handler: Handler,
        event: TelegramObject,
        data: EventData,
    ) -> Any:
        """Перехватывает событие и 
        засекает время обработки."""

        if not isinstance(event, Update):
            return await handler(event, data)

        action = data.get("action_type", "unknown")
        start_at = perf_counter()
        error = None

        try:
            return await handler(event, data)
        except Exception as exc:
            error = exc
            raise

        finally:
            self._log(
                action=action,
                upd_id=event.update_id,
                elapsed=perf_counter() - start_at,
                error=error
            )