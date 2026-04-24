from typing import Final, final

from . import inline as _inline
from . import reply as _reply


@final
class KeyboardFacade:
    """Фасад для доступа
    к клавиатурам."""

    __slots__ = ()
    inline = _inline
    reply = _reply


# Единый экземпляр
# для использования.
kb: Final = KeyboardFacade()