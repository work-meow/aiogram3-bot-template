from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram_i18n import I18nContext

from app.bot.filters import ThreadFilter


router = Router(name="topic")


@router.message(Command("topic"), ThreadFilter())
async def cmd_topic(msg: Message, i18n: I18nContext) -> None:
    """Срабатывает только в топиках форума.
    Ответ уходит в тот же топик автоматически
    (aiogram проставляет message_thread_id)."""

    await msg.answer(i18n.get(
        "topic-hello", 
        id=msg.message_thread_id
    ))
