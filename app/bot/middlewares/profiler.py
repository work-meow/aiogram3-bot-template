from typing import Any
from time import perf_counter
from aiogram import BaseMiddleware
from collections.abc import Awaitable, Callable
from aiogram.types import TelegramObject, Update
from loguru import logger



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


    @staticmethod
    def _event_type(event: Update) -> str:
        """Безопасно извлекает тип
        события из апдейта."""
        try:
            return event.event_type
        except LookupError:
            return "unknown"


    def _log(
        self,
        event: Update,
        elapsed: float,
        error: Exception | None,
    ) -> None:
        """Записывает информацию об
        обработке апдейта в логи."""

        update_id = event.update_id
        event_type = self._event_type(event)

        if error is not None and self.log_errors:
            logger.opt(exception=error).error(
                "UPDATE ERROR | update_id={} "
                "| type={} | elapsed={:.3f}s",
                update_id,
                event_type,
                elapsed,
            )
            return

        if elapsed >= self.slow_after:
            logger.warning(
                "SLOW UPDATE | update_id={} "
                "| type={} | elapsed={:.3f}s",
                update_id,
                event_type,
                elapsed,
            )
            return

        if self.log_fast:
            logger.debug(
                "UPDATE TIME | update_id={} "
                "| type={} | elapsed={:.3f}s",
                update_id,
                event_type,
                elapsed,
            )


    async def __call__(
        self,
        handler: Handler,
        event: TelegramObject,
        data: EventData,
    ) -> Any:
        """Точка входа: перехватывает событие
        и засекает время обработки."""

        if not isinstance(event, Update):
            return await handler(event, data)

        started_at = perf_counter()
        error = None

        try:
            return await handler(event, data)

        except Exception as exc:
            error = exc
            raise

        finally:
            self._log(
                event=event,
                elapsed=perf_counter() - started_at,
                error=error
            )
