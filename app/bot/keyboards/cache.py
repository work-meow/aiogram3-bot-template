from threading import Lock
from functools import wraps
from collections import OrderedDict
from typing import Any, Concatenate, ParamSpec, TypeVar
from inspect import Signature, iscoroutinefunction, signature
from collections.abc import Callable, Hashable, Mapping
from aiogram.filters.callback_data import CallbackData
from aiogram_i18n import I18nContext


P = ParamSpec("P")
R = TypeVar("R")

_PRIMITIVE_TYPES = (
    str, int, float,
    bool, bytes,
    type(None),
)


def _freeze(value: Any) -> Hashable:
    """
    Преобразует параметр клавиатуры в hashable-ключ.
    Поддерживаем типы, которые нормально использовать
    в фабриках клавиатур: примитивы, CallbackData,
    списки, кортежи и словари.
    """

    if isinstance(value, CallbackData):
        return (type(value), value.pack())

    if isinstance(value, _PRIMITIVE_TYPES):
        return (type(value), value)

    if isinstance(value, (tuple, list)):
        return tuple(_freeze(item) for item in value)

    if isinstance(value, Mapping):
        return tuple(
            sorted(
                (
                    (_freeze(key), _freeze(item))
                    for key, item in value.items()
                ),
                key=repr,
            )
        )

    if isinstance(value, Hashable):
        return (type(value), value)

    raise TypeError(
        "Cannot cache keyboard with non-hashable argument "
        f"{type(value).__module__}.{type(value).__qualname__}. "
        "Use primitive values, CallbackData, lists, tuples or dicts."
    )


def _make_key(
    sig: Signature,
    i18n: I18nContext,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Hashable:
    """Собирает ключ кэша из локали
    и нормализованных аргументов."""

    locale = getattr(i18n, "locale", None)
    if locale is None:
        raise ValueError(
            "I18nContext must contain a "
            "valid 'locale' attribute."
        )

    bound = sig.bind(
        i18n, *args,
        **kwargs
    )

    bound.apply_defaults()
    args = tuple(bound.arguments.items())

    return (
        str(locale), tuple(
            (name, _freeze(value))
            for name, value
            in args[1:]
        ),
    )


def cached_kb(
    *,
    maxsize: int | None = 256,
) -> Callable[
    [Callable[Concatenate[I18nContext, P], R]],
    Callable[Concatenate[I18nContext, P], R],
]:
    """
    LRU-кэш для синхронных фабрик клавиатур.

    maxsize=None — для статичных клавиатур:
    main_menu, back, close, cancel.

    maxsize=N — для параметризованных клавиатур:
    catalog_page, language_menu, filters.
    """

    if maxsize is not None and maxsize < 1:
        raise ValueError(
            "maxsize must be a positive "
            "integer or None."
        )

    def decorator(
        func: Callable[Concatenate[I18nContext, P], R],
    ) -> Callable[Concatenate[I18nContext, P], R]:

        if iscoroutinefunction(func):
            raise TypeError(
                "@cached_kb supports only sync "
                "keyboard factories."
            )

        lock = Lock()
        cache: OrderedDict[Hashable, R] = OrderedDict()
        sig = signature(func)

        @wraps(func)
        def wrapper(
            i18n: I18nContext,
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> R:

            key = _make_key(
                sig, i18n, args,
                kwargs
            )

            with lock:
                if key in cache:
                    cache.move_to_end(key)
                    return cache[key]

                result = func(
                    i18n, *args,
                    **kwargs
                )

                cache[key] = result
                if maxsize is not None and len(cache) > maxsize:
                    cache.popitem(last=False)
                return result

        return wrapper

    return decorator