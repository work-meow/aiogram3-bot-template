from html import escape
from aiogram import Router
from aiogram.types import Message
from aiogram_i18n import I18nContext
from aiogram.filters import CommandStart
from dishka.integrations.aiogram import FromDishka
from sqlalchemy.ext.asyncio import AsyncSession

from app.storage.models import User
from app.bot.keyboards import kb



router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(
    msg: Message,
    i18n: I18nContext,
    user: User,
    session: FromDishka[AsyncSession],
) -> None:
    """Обработка команды /start."""

    name = escape(
        user.full_name or i18n.get("guest-name"),
        quote=False
    )

    await msg.answer(
        text=i18n.get('welcome-text', name=name),
        reply_markup=kb.reply.main_menu(i18n),
    )
