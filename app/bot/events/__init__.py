from aiogram import Dispatcher

from .startup import on_startup
from .shutdown import on_shutdown
from .fsm_sync import load_fsm, save_fsm
from .metrics_sync import load_stats, save_stats
from .errors import on_error
from .member import on_chat



def setup_events(dp: Dispatcher) -> None:
    """Регистрация всех системных 
    событий бота (Lifecycle & Errors)"""
    
    # --- СТАРТ БОТА ---
    dp.startup.register(load_fsm)
    dp.startup.register(load_stats)
    dp.startup.register(on_startup)    
    
    
    # --- СИСТЕМНЫЕ СОБЫТИЯ ---
    dp.errors.register(on_error) 
    dp.my_chat_member.register(on_chat) 


    # --- ОСТАНОВКА БОТА ---
    dp.shutdown.register(save_fsm)
    dp.shutdown.register(save_stats) 
    dp.shutdown.register(on_shutdown) 