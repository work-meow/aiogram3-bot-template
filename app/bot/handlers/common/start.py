from html import escape
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram_i18n import I18nContext

from app.bot.keyboards import kb


router = Router(name="start")

@router.message(CommandStart())
async def cmd_start(
    msg: Message,
    i18n: I18nContext,
) -> None:
    """Обработка команды
    /start."""

    raw = (
        msg.from_user.full_name.strip()
        if msg.from_user
        else ""
    )

    name = escape(
        raw or i18n.get("guest-name"),
        quote=False
    )

    await msg.answer(
        text=i18n.get("welcome-text", "ru", name=name),
        reply_markup=kb.reply.main_menu(i18n),
    )