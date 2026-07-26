from typing import Any
from html import escape
from datetime import datetime



class Safe(str):
    """Готовая разметка
    повторно не эскейпится."""


def _esc(val: Any) -> str:
    """Эскейпит текст юзера, но
    не разметку, собранную 
    функциями ниже ."""

    if isinstance(val, Safe):
        return val
    return escape(str(val), quote=False)


def _attr(val: Any) -> str:
    """Значение внутрь HTML-атрибута."""
    return escape(str(val), quote=True)


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
def link(url: str, txt: Any) -> Safe:
    """Обычная гиперссылка."""
    return Safe(f'<a href="{_attr(url)}">{_esc(txt)}</a>')

def mention(txt: Any, user_id: int | str) -> Safe:
    """Кликабельное упоминание юзера без @username."""
    return Safe(f'<a href="tg://user?id={_attr(user_id)}">{_esc(txt)}</a>')

def code(txt: Any) -> Safe:
    """Моноширинный текст."""
    return Safe(f"<code>{_esc(txt)}</code>")

def pre(txt: Any) -> Safe:
    """Блок кода."""
    return Safe(f"<pre>{_esc(txt)}</pre>")

def bold(txt: Any) -> Safe:
    """Жирный текст."""
    return Safe(f"<b>{_esc(txt)}</b>")

def italic(txt: Any) -> Safe:
    """Курсив."""
    return Safe(f"<i>{_esc(txt)}</i>")

def underline(txt: Any) -> Safe:
    """Подчеркнутый текст."""
    return Safe(f"<u>{_esc(txt)}</u>")

def strike(txt: Any) -> Safe:
    """Зачеркнутый текст."""
    return Safe(f"<s>{_esc(txt)}</s>")

def spoiler(txt: Any) -> Safe:
    """Скрытый текст."""
    return Safe(f"<tg-spoiler>{_esc(txt)}</tg-spoiler>")

def quote(txt: Any) -> Safe:
    """Блочная цитата."""
    return Safe(f"<blockquote>{_esc(txt)}</blockquote>")

def emoji(emoji_id: str | int, fallback: Any) -> Safe:
    """Премиум кастомный эмодзи. fallback — обычный юникод-эмодзи,
    который увидят юзеры без Premium и клиенты без поддержки."""
    return Safe(f'<tg-emoji emoji-id="{_attr(emoji_id)}">{_esc(fallback)}</tg-emoji>')