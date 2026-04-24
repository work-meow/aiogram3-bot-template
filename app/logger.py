import sys
import logging
import logging_loki

from loguru import logger
from .settings import get_settings


LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "[<cyan>{name}:{function}:{line}</cyan>] - <level>{message}</level>"
)


def setup_logger():
    # 1. Сбрасываем дефолтный
    logger.remove()

    # 2. Настраиваем обработчики
    # (консоль и файл)
    handlers =[
        {
            "sink": sys.stdout,
            "format": LOG_FORMAT,
            "level": get_settings().LOG_LEVEL,
            "backtrace": True,
            "diagnose": True,
            "enqueue": True,
        },
        {

            "format": LOG_FORMAT,
            "level": get_settings().LOG_LEVEL,
            "sink": "logs/{time:YYYY-MM}/{time:YYYY-MM-DD}.log",
            "rotation": "10 MB",
            "retention": "7 days",
            "encoding": "utf-8",
            "enqueue": True,
        },
    ]

    # Применяем конфигурацию
    logger.configure(handlers=handlers)

    # 3. Пытаемся подключить Loki
    if getattr(get_settings(), "LOKI_URL", None):
        try:
            # Инициализируем клиент Loki
            loki_handler = logging_loki.LokiHandler(
                url=get_settings().LOKI_URL,
                version="1",
                tags={
                    "application": get_settings().SRVC_NAME,
                    "service": get_settings().SRVC_NAME
                },
                auth=(
                    get_settings().LOKI_USER,
                    get_settings().LOKI_PASS
                ),
            )

            # Мини-адаптер: формат Loguru в Loki
            def loki_sink(message):
                record = logging.LogRecord(
                    name=message.record["name"],
                    level=message.record["level"].no,
                    pathname=message.record["file"].path,
                    exc_info=message.record["exception"],
                    lineno=message.record["line"],
                    msg=str(message).strip(),
                    args=()
                )
                loki_handler.emit(record)

            # Добавляем Loki
            logger.add(
                sink=loki_sink,
                level=get_settings().LOG_LEVEL,
                enqueue=True
            )

        except Exception as e:
            logger.error(f"Failed to initialize Loki: {e}")

    logger.info("Логгер успешно настроен")