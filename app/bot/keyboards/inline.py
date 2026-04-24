# fmt: off
# isort: off
from aiogram_i18n import I18nContext
from aiogram.types import InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData

from ..callbacks import NavAction, NavCb
from .builders import I18nInline
from .cache import cached_kb


CbValue = str | CallbackData


@cached_kb(maxsize=256)
def back(
    i18n: I18nContext,
    cb: CbValue = NavCb(
        action=NavAction.back
    ),
) -> InlineKeyboardMarkup:
    """Инлайн-клавиатура
    с кнопкой назад."""

    return (
        I18nInline(i18n)
        .btn("btn-back", cb)
        .adjust(1)
        .as_markup()
    )



@cached_kb(maxsize=256)
def close(
    i18n: I18nContext,
    cb: CbValue = NavCb(
        action=NavAction.close
    ),
) -> InlineKeyboardMarkup:
    """Инлайн-клавиатура
    с кнопкой закрыть."""

    return (
        I18nInline(i18n)
        .btn("btn-close", cb)
        .adjust(1)
        .as_markup()
    )



@cached_kb(maxsize=256)
def cancel(
    i18n: I18nContext,
    cb: CbValue = NavCb(
        action=NavAction.cancel
    ),
) -> InlineKeyboardMarkup:
    """Инлайн-клавиатура
    с кнопкой отмена."""

    return (
        I18nInline(i18n)
        .btn("btn-cancel", cb)
        .adjust(1)
        .as_markup()
    )