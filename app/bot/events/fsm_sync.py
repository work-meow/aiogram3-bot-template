from loguru import logger
from itertools import batched
from aiogram import Dispatcher
from dishka import AsyncContainer
from aiogram.fsm.storage.base import StorageKey
from dishka.integrations.aiogram import FromDishka, inject
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.storage.memory import (
    MemoryStorageRecord,
    MemoryStorage
)


from app.storage import StorageState



@inject
async def load_fsm(
    dispatcher: Dispatcher,
    container: FromDishka[AsyncContainer]
) -> None:
    """Восстановление свежих 
    стейтов в память."""
    
    # 1. Только при
    # оперативной памяти
    stg = dispatcher.fsm.storage
    if not isinstance(stg, MemoryStorage):
        return
    
    # 2. Получаем активные 
    # сессии состояний из БД
    async with container() as cont:
        db = await cont.get(AsyncSession)
        res = await StorageState.get_active(db)
        
    states = {
        StorageKey(
            bot_id=s.bot_id, 
            chat_id=s.chat_id, 
            user_id=s.user_id, 
            destiny=s.destiny
        ): MemoryStorageRecord(
            state=s.state,
            data=s.data
        )
        for s in res
    }
    
    # 4. Заливаем данные 
    # во внутренний словарь
    stg.storage.update(states)
    logger.debug(f"FSM Load: {len(states)}")




@inject
async def save_fsm(
    dispatcher: Dispatcher,
    container: FromDishka[AsyncContainer]
) -> None:
    """Пакетное сохранение 
    состояний в БД (UPSERT)."""
    
    # 1. Проверяем хранилище и 
    # отсекаем пустые вызовы
    stg = dispatcher.fsm.storage
    if not isinstance(stg, MemoryStorage):
        return
    
    if not stg.storage:
        return
    
    # 2. Сортируем на 
    # сохранение и удаление
    to_del, to_upd = [], []
    for key, rec in stg.storage.items():
        if rec.state is None and not rec.data:
            to_del.append((
                key.bot_id, 
                key.chat_id, 
                key.user_id, 
                key.destiny
            ))
        else:
            to_upd.append({
                "bot_id": key.bot_id, 
                "chat_id": key.chat_id,
                "user_id": key.user_id, 
                "destiny": key.destiny,
                "state": rec.state, 
                "data": rec.data,
            })
  
    # 3. Открываем транзакцию БД
    async with container() as cont:
        db = await cont.get(AsyncSession)
        
        # 4. Удаляем завершенные
        for chunk in batched(to_del, 5000):
            await StorageState.bulk_delete(
                db, list(chunk)
            )
            
        # 5. Сохраняем активные
        for chunk in batched(to_upd, 5000):
            await StorageState.bulk_upsert(
                db, list(chunk)
            )

        # 6. Запускаем сборщик мусора 
        await StorageState.cleanup(db)
        await db.commit()
    
    logger.debug(
        "💾 FSM synced in bd: "
        f"{len(to_upd)} saved, "
        f"{len(to_del)} dropped"
    )