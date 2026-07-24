from typing import Any
from aiogram.types import InputRichMessage, Message, ReplyMarkupUnion
from aiogram_i18n import I18nContext


async def answer_rich(
    msg: Message,
    i18n: I18nContext,
    key: str,
    *,
    reply_markup: ReplyMarkupUnion | None = None,
    is_rtl: bool | None = None,
    **vars: Any,
) -> Message:
    """Rich-ответ из локали: HTML
    собирается тем же Fluent-конвейером,
    что и обычные сообщения и уходит как rich.
    `vars` — подстановки Fluent, всё остальное
    параметры отправки."""

    return await msg.answer_rich(
        rich_message=InputRichMessage(
            html=i18n.get(key, **vars),
            is_rtl=is_rtl
        ),
        reply_markup=reply_markup,
    )
