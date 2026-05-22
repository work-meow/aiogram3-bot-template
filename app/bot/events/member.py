from aiogram import Bot
from loguru import logger
from aiogram.enums import ChatMemberStatus
from aiogram.types import ChatMemberUpdated
from dishka.integrations.aiogram import FromDishka

from app.settings import Settings



OLD = frozenset((
    ChatMemberStatus.LEFT, 
    ChatMemberStatus.KICKED
))

NEW = frozenset((
    ChatMemberStatus.MEMBER, 
    ChatMemberStatus.ADMINISTRATOR
))



async def on_chat(
    event: ChatMemberUpdated,
    bot: FromDishka[Bot],
    settings: FromDishka[Settings]
) -> None:
    """Отслеживаем добавление 
    бота в новые чаты."""
    
    if (
        event.old_chat_member.status not in OLD 
        or event.new_chat_member.status not in NEW
    ): 
        return

    chat, user = event.chat, event.from_user
    title = chat.title or str(chat.id)
    
    if not settings.LOG_CHAT:
        return

    try:
        await bot.send_message(
            chat_id=settings.LOG_CHAT,
            text=(
                f"<b>Новый чат!</b>\n\n"
                f"<b>Название:</b> {name}\n"
                f"<b>Тип:</b> {c.type}\n"
                f"<b>ID:</b> {c.id}\n"
            )
        )
        
    except Exception as e:
        logger.error(f"❌ Member alert: {e}")
