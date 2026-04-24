from typing import Any, Self

from aiogram_i18n import I18nContext
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import (
    KeyboardButtonPollType,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    CopyTextButton,
    WebAppInfo,
    LoginUrl
)


class I18nInline(InlineKeyboardBuilder):
    """Инлайн-клавиатуры с автопереводом (Fluent Builder)."""

    def __init__(self, i18n: I18nContext) -> None:
        super().__init__()
        self.i18n = i18n

    def url(self, key: str, url: str, **kwargs: Any) -> Self:
        self.button(text=self.i18n.get(key, **kwargs), url=url)
        return self

    def pay(self, key: str, **kwargs: Any) -> Self:
        self.button(text=self.i18n.get(key, **kwargs), pay=True)
        return self

    def btn(self, key: str, cd: str | CallbackData, **kwargs: Any) -> Self:
        self.button(text=self.i18n.get(key, **kwargs), callback_data=cd)
        return self

    def web_app(self, key: str, url: str, **kwargs: Any) -> Self:
        self.button(text=self.i18n.get(key, **kwargs), web_app=WebAppInfo(url=url))
        return self

    def login(self, key: str, url: str, **kwargs: Any) -> Self:
        self.button(text=self.i18n.get(key, **kwargs), login_url=LoginUrl(url=url))
        return self

    def copy(self, key: str, copy_text: str, **kwargs: Any) -> Self:
        self.button(text=self.i18n.get(key, **kwargs), copy_text=CopyTextButton(text=copy_text))
        return self

    def as_markup(self, **kwargs: Any) -> InlineKeyboardMarkup:
        return super().as_markup(**kwargs)



class I18nReply(ReplyKeyboardBuilder):
    """Reply-клавиатуры с автопереводом и UX-оптимизацией."""

    def __init__(self, i18n: I18nContext) -> None:
        super().__init__()
        self.i18n = i18n

    def btn(self, key: str, **kwargs: Any) -> Self:
        self.button(text=self.i18n.get(key, **kwargs))
        return self

    def contact(self, key: str, **kwargs: Any) -> Self:
        self.button(text=self.i18n.get(key, **kwargs), request_contact=True)
        return self

    def location(self, key: str, **kwargs: Any) -> Self:
        self.button(text=self.i18n.get(key, **kwargs), request_location=True)
        return self

    def web_app(self, key: str, url: str, **kwargs: Any) -> Self:
        self.button(text=self.i18n.get(key, **kwargs), web_app=WebAppInfo(url=url))
        return self

    def poll(self, key: str, type: str = "regular", **kwargs: Any) -> Self:
        self.button(text=self.i18n.get(key, **kwargs), request_poll=KeyboardButtonPollType(type=type))
        return self

    def as_markup(self, *, resize_keyboard: bool = True, **kwargs: Any) -> ReplyKeyboardMarkup:
        return super().as_markup(resize_keyboard=resize_keyboard, **kwargs)