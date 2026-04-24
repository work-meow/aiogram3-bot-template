from enum import Enum
from aiogram.filters.callback_data import CallbackData


class NavAction(str, Enum):
    back = "back"
    close = "close"
    cancel = "cancel"


class NavCb(CallbackData, prefix="nav"):
    action: NavAction