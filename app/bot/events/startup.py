from aiogram import Bot
from loguru import logger
from dishka.integrations.aiogram import FromDishka, inject

from app.settings import Settings


@inject
async def on_startup(
    bot: FromDishka[Bot],
    settings: FromDishka[Settings]
) -> None:
    """Уведомление о старте."""

    me = await bot.get_me()
    logger.info(f"🚀 Bot @{me.username}")

    if not (chat_id := settings.LOG_CHAT):
        return logger.warning(
            "⚠️ LOG_CHAT is "
            "missing."
        )

    try:
        await bot.send_message(
            chat_id=chat_id,
            text="🟢 Service online"
        )

    except Exception as e:
        logger.error(f"❌ Startup alert: {e}")