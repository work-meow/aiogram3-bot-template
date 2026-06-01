from prometheus_client import (
    CollectorRegistry, 
    Histogram,
    Counter,
)


# Изолированный реестр 
# для всего проекта
registry = CollectorRegistry()


# 1. Счетчик активности
# Команды бота, API и др
ACTIONS = Counter(
    name="ACTIONS_total",
    documentation="Количество обработанных действий",
    labelnames=["service", "action_type"],
    registry=registry
)


# 2. Счетчик ошибок
ERRORS = Counter(
    name="ERRORS_total",
    documentation="Количество возникших ошибок",
    labelnames=["service", "error_type"],
    registry=registry
)


# 3. Измеритель скорости
DURATION = Histogram(
    name="system_processing_seconds",
    documentation="Время выполнения действия",
    labelnames=["service", "action_type"],
    registry=registry
)


# Маппинг 
# счетчиков
# для O(1) поиска 
COUNTERS = {
    "ACTIONS_total": ACTIONS,
    "ERRORS_total": ERRORS,
}