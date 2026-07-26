from loguru import logger
from sqlalchemy import event
from sqlalchemy.engine import Engine
from time import perf_counter


SLOW_DB_SEC = 0.5


def trace_sql(engine: Engine) -> None:
    """Мониторинг долгих SQL-запросов."""


    @event.listens_for(engine, "before_cursor_execute")
    def before_exec(_c, _cr, _q, _p, ctx, _m) -> None:
        ctx._start = perf_counter()


    @event.listens_for(engine, "after_cursor_execute")
    def after_exec(_c, _cr, q, _p, ctx, _m) -> None:
        duration = perf_counter() - ctx._start

        if duration >= SLOW_DB_SEC:
            logger.warning(f"🐌 {duration:.3f}с | {q}")
