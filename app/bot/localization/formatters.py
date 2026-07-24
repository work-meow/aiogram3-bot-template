from typing import Any
from datetime import datetime


# ----- Финансы и числа -----
def fmt_money(val: int | float) -> str:
    """10000.5 -> 10 000.50"""
    return f"{val:,.2f}".replace(",", " ")

def fmt_num(val: int | float) -> str:
    """1000000 -> 1 000 000"""
    return f"{val:,}".replace(",", " ")

def pct(val: float) -> str:
    """0.155 -> 15.5%"""
    return f"{val * 100:.1f}%"



# ----- Даты и время -----
def _to_dt(dt: datetime | int) -> datetime:
    return datetime.fromtimestamp(dt) if isinstance(dt, int) else dt

def fmt_date(dt: datetime | int) -> str:
    return _to_dt(dt).strftime("%d.%m.%Y")

def fmt_time(dt: datetime | int) -> str:
    return _to_dt(dt).strftime("%H:%M")

def fmt_dt(dt: datetime | int) -> str:
    return _to_dt(dt).strftime("%d.%m.%Y %H:%M")



# ----- Текст -----
def trunc(txt: str, limit: int = 30) -> str:
    return txt[:limit] + "..." if len(txt) > limit else txt

def phone(num: str | int) -> str:
    """79991234567 -> +7 999 123-45-67"""
    s = str(num).replace("+", "").strip()
    return f"+{s[0]} {s[1:4]} {s[4:7]}-{s[7:9]}-{s[9:11]}" if len(s) == 11 else f"+{s}"



# ----- HTML разметка -----
def link(url: str, txt: Any) -> str:
    """Обычная гиперссылка."""
    return f'<a href="{url}">{txt}</a>'

def mention(txt: Any, user_id: int | str) -> str:
    """Кликабельное упоминание юзера без @username."""
    return f'<a href="tg://user?id={user_id}">{txt}</a>'

def code(txt: Any) -> str:
    """Моноширинный текст."""
    return f"<code>{txt}</code>"

def pre(txt: Any) -> str:
    """Блок кода."""
    return f"<pre>{txt}</pre>"

def bold(txt: Any) -> str:
    """Жирный текст."""
    return f"<b>{txt}</b>"

def italic(txt: Any) -> str:
    """Курсив."""
    return f"<i>{txt}</i>"

def underline(txt: Any) -> str:
    """Подчеркнутый текст."""
    return f"<u>{txt}</u>"

def strike(txt: Any) -> str:
    """Зачеркнутый текст."""
    return f"<s>{txt}</s>"

def spoiler(txt: Any) -> str:
    """Скрытый текст."""
    return f"<tg-spoiler>{txt}</tg-spoiler>"

def quote(txt: Any) -> str:
    """Блочная цитата."""
    return f"<blockquote>{txt}</blockquote>"

def emoji(emoji_id: str | int, fallback: Any) -> str:
    """Премиум кастомный эмодзи. fallback — обычный юникод-эмодзи,
    который увидят юзеры без Premium и клиенты без поддержки."""
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'