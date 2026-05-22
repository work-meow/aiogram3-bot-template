from aiogram import Dispatcher

from .startup import on_startup
from .shutdown import on_shutdown
from .fsm_sync import load_fsm, save_fsm
from .errors import on_error
from .member import on_chat


def setup_events(dp: Dispatcher) -> None:
    """Подключение системных 
    эвентов к диспетчеру."""
    
    dp.startup.register(load_fsm)            
    dp.startup.register(on_startup)          
    
    dp.shutdown.register(save_fsm)           
    dp.shutdown.register(on_shutdown)  
    
    dp.my_chat_member.register(on_chat)
    dp.errors.register(on_error)          