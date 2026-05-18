import html
import traceback

from aiogram import Bot
from loguru import logger
from aiogram.types import BufferedInputFile, ErrorEvent
from dishka.integrations.aiogram import FromDishka, inject

from app.settings import Settings



def get_ids(
    event: ErrorEvent
) -> tuple[int | str, int | str]:
    """Извлекает update_id и
    user_id из события."""

    if not (upd := event.update):
        return "unknown", "unknown"

    try:
        return (
            upd.update_id,
            upd.event.from_user.id
        )
    except AttributeError:
        return upd.update_id, "unknown"




def tb_file(
    exc: BaseException,
    upd_id: int | str
) -> BufferedInputFile:
    """Создаёт файл с
    трейсбеком."""

    tb = "".join(
        traceback.format_exception(
            tb=exc.__traceback__,
            etype=type(exc),
            value=exc,
        )
    )

    return BufferedInputFile(
        file=tb.encode(),
        filename=f"er_{upd_id}.txt"
    )




def caption(
    upd_id: int | str,
    user_id: int | str,
    exc: BaseException
) -> str:
    """Создаёт caption
    для уведомления."""

    name = html.escape(type(exc).__name__)
    msg = html.escape(str(exc)[:200])

    return (
        f"⚠️ <b>Сбой обработчика</b>\n\n"
        f"👤 <b>User:</b> <code>{user_id}</code>\n"
        f"🔄 <b>Update:</b> <code>{upd_id}</code>\n"
        f"🛑 <b>Type:</b> <code>{name}</code>\n"
        f"💬 <b>Msg:</b> <code>{msg}</code>"
    )




@inject
async def on_error(
    event: ErrorEvent,
    bot: FromDishka[Bot],
    settings: FromDishka[Settings],
) -> None:
    """Глобальный перехват
    ошибок aiogram."""

    exc = event.exception
    upd_id, user_id = get_ids(event)
    logger.opt(exception=exc).error(
        f"Сбой апдейта {upd_id} "
        f"| user={user_id}"
    )

    try:
        if not settings.LOG_CHAT:
            return

        await bot.send_document(
            chat_id=settings.LOG_CHAT,
            document=tb_file(exc, upd_id),
            caption=caption(upd_id, user_id, exc),
        )

    except Exception as e:
        logger.opt(exception=e).warning(
            "Не удалось отправить "
            "уведомление в лог-чат"
        )
