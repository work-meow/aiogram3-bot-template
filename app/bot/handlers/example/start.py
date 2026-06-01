from html import escape
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram_i18n import I18nContext
from dishka.integrations.aiogram import FromDishka
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.bot.keyboards import kb
from app.storage.models import User


router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(
    msg: Message,
    i18n: I18nContext,
    user: User,
    session: FromDishka[AsyncSession],
) -> None:
    """Обработка команды /start."""

    total_users = await session.scalar(
        select(func.count()).select_from(User)
    )

    name = escape(
        user.full_name or i18n.get("guest-name"),
        quote=False
    )

    await msg.answer(
        text=f"{i18n.get('welcome-text', name=name)}\n\n"
             f"📊 Всего юзеров в БД: {total_users}",
        reply_markup=kb.reply.main_menu(i18n),
    )
