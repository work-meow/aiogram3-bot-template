import html
import traceback

from aiogram import Bot
from loguru import logger
from aiogram.types import BufferedInputFile, ErrorEvent, Update, User
from dishka.integrations.aiogram import FromDishka, inject

from app.settings import Settings


@inject
async def on_error(
    event: ErrorEvent,
    bot: FromDishka[Bot],
    settings: FromDishka[Settings]
) -> None:
    """Глобальный перехват ошибок."""

    exc: Exception = event.exception
    update: Update | None = event.update

    # 1. Извлекаем данные события
    user: User | None = getattr(getattr(update, "event", None), "from_user", None)
    upd_id: int | str  = update.update_id if update else "unknown"
    user_id: int | str  = user.id if user else "unknown"

    # 2. Логгируем в консоль и файл
    logger.opt(exception=exc).error(f"💥 Сбой апдейта {upd_id} (User: {user_id})")

    # 3. Проверяем лог-чат
    chat_id = settings.LOG_CHAT
    if not chat_id:
        return

    # 4. Экранируем текст для безопасного парсинга
    exc_type: str = html.escape(type(exc).__name__)
    exc_msg: str = html.escape(str(exc))[:200]

    # 5. Подготовка файла в памяти
    tb_str: str = "".join(traceback.format_exception(exc))
    tb_file: BufferedInputFile = BufferedInputFile(
        file=tb_str.encode("utf-8"),
        filename=f"error_{upd_id}.txt"
    )

    # 6. Отправка уведомления с файлом
    try:
        await bot.send_document(
            chat_id=chat_id,
            document=tb_file,
            caption=(
                f"⚠️ <b>Сбой обработчика</b>\n\n"
                f"👤 <b>User:</b> <code>{user_id}</code>\n"
                f"🔄 <b>Update:</b> <code>{upd_id}</code>\n"
                f"🛑 <b>Type:</b> <code>{exc_type}</code>\n"
                f"💬 <b>Msg:</b> <code>{exc_msg}...</code>"
            )
        )
    except Exception as e:
        logger.error(f"❌ Сбой уведомления: {e}")