from aiogram import Dispatcher

from .startup import on_startup
from .shutdown import on_shutdown
from .member import on_chat_join
from .errors import on_error



def setup_events(dp: Dispatcher) -> None:
    """Подключение системных 
    эвентов к диспетчеру."""
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.my_chat_member.register(on_chat_join)
    dp.errors.register(on_error)
