# fmt: off
# isort: off
from aiogram_i18n import I18nContext
from aiogram.types import ReplyKeyboardMarkup

from .builders import I18nReply
from .cache import cached_kb



@cached_kb(maxsize=None)
def main_menu(
    i18n: I18nContext,
) -> ReplyKeyboardMarkup:
    """Главное нижнее меню бота
    (реплай-клавиатура)."""

    return (
        I18nReply(i18n)
        .btn("reply-home")
        .btn("reply-help")
        .adjust(1, 1)
        .as_markup()
    )