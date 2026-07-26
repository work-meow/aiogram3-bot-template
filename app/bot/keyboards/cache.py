from functools import wraps
from collections import OrderedDict
from inspect import iscoroutinefunction
from collections.abc import Callable, Hashable, Mapping
from typing import Any, Concatenate, ParamSpec, TypeVar
from aiogram.filters.callback_data import CallbackData
from aiogram_i18n import I18nContext
from loguru import logger


P = ParamSpec("P")
R = TypeVar("R")

PRIMITIVES = (
    str | int | float 
    | bool | bytes | 
    type(None)
)




def _freeze(val: Any) -> Hashable:
    """Рекурсивная заморозка 
    аргументов в hash-ключ."""
    
    # 1. Примитивы
    if isinstance(val, PRIMITIVES):
        return (val.__class__, val)

    # 2. CallbackData
    if isinstance(val, CallbackData):
        return (val.__class__, val.pack())

    # 3. Коллекции (кортежи, списки)
    if isinstance(val, tuple | list):
        return tuple(map(_freeze, val))

    # 4. Словари (через frozenset)
    if isinstance(val, Mapping):
        return frozenset(
            (_freeze(k), _freeze(v))
            for k, v in val.items()
        )

    # 5. Остальные объекты
    if isinstance(val, Hashable):
        return (val.__class__, val)

    # 6. Некэшируемое
    raise TypeError(
        "Uncacheable arg: "
        f"{val.__class__.__module__}."
        f" {val.__class__.__qualname__}"
    )




def _detach[T](val: T) -> T:
    """Отдаёт копию структуры 
    разметки.."""

    for field in ("inline_keyboard", "keyboard"):
        if (rows := getattr(val, field, None)) is None:
            continue

        copy = val.model_copy()
        setattr(copy, field, [list(row) for row in rows])
        return copy

    return val




def _make_key(
    i18n: I18nContext,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> tuple[str, Hashable, Hashable]:
    """Прямая сборка ключа."""
    
    if not (
        locale := getattr(
            i18n, "locale",
            None
        )
    ):
        raise ValueError(
            "I18nContext missing "
            "'locale' attribute."
        )

    return (
        locale,
        _freeze(args),
        _freeze(kwargs),
    )




def cached_kb(
    *,
    maxsize: int = 256,
) -> Callable[
    [Callable[Concatenate[I18nContext, P], R]],
    Callable[Concatenate[I18nContext, P], R],
]:
    """LRU-кэш синхронных фабрик клавиатур.
    maxsize обязателен: без предела фабрика
    с аргументами копила бы запись на каждое
    их значение — это прямая утечка."""

    if not isinstance(maxsize, int) or maxsize < 1:
        raise ValueError("maxsize must be int >= 1")

    def decorator(
        func: Callable[Concatenate[I18nContext, P], R]
    ) -> Callable[Concatenate[I18nContext, P], R]:
        
        if iscoroutinefunction(func):
            raise TypeError(
                "Supports only "
                "sync factories."
            )

        # Кэш + лок. кэш методов для ускорения
        cache: OrderedDict[Hashable, R] = OrderedDict()
        _move_to_end = cache.move_to_end
        _popitem = cache.popitem

        @wraps(func)
        def wrapper(
            i18n: I18nContext,
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> R:
            
            # 1. Получаем ключ
            k_key = _make_key(
                i18n, args, 
                kwargs
            )

            # 2. Берем из кэша
            if k_key in cache:
                _move_to_end(k_key)
                return _detach(cache[k_key])

            # 3. Вып. фабрику
            result = func(
                i18n, *args,
                **kwargs
            )

            # 4. Контроль лимита
            cache[k_key] = result
            if len(cache) > maxsize:
                _popitem(last=False)

            # Копию отдаём и на промахе: иначе
            # первый вызывающий получит сам
            # закэшированный объект
            return _detach(result)

        return wrapper

    return decorator