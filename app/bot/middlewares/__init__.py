from aiogram import Dispatcher

from .logging import LoggingMiddleware
from .profiler import ProfilerMiddleware
from .throttling import ThrottlingMiddleware
from .autoanswer  import AutoAnswerMiddleware
from app.bot.localization import setup_i18n


def setup_middlewares(dp: Dispatcher) -> None:
    """Регистрация всех мидлварей."""

    # 1. Профилер времени обработки
    dp.update.outer_middleware(ProfilerMiddleware(slow=1.5))

    # 2. Локализация текстов
    setup_i18n().setup(dispatcher=dp)

    # 3. Сбор контекста (FSM и логи)
    dp.update.middleware(LoggingMiddleware())

    # 4. Защита от спама (только для сообщений и кнопок)
    dp.message.middleware(ThrottlingMiddleware(rate_limit=0.5))
    dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=0.5))

    # 5. Автоматический ответ на коллбеки
    dp.callback_query.middleware(AutoAnswerMiddleware())