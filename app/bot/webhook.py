import hmac
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher, types
from fastapi import (
APIRouter, 
Header, 
HTTPException,
Request, 
BackgroundTasks
)

from app.settings import Settings



@asynccontextmanager
async def bot_lifespan(
    bot: Bot, 
    dp: Dispatcher, 
    settings: Settings
) -> AsyncIterator[None]:
    """Lifespan-контекст: безопасная
    установка и очистка вебхука."""


    # 1. Fail-fast проверка: 
    # падаем до старта приложения
    if not settings.BOT_SECRET:
        raise ValueError(
            "Критическая ошибка: " 
            "BOT_SECRET пуст!"
        )

    _data = {
        "bots": (bot,),       
        "dispatcher": dp,     
        **dp.workflow_data,
    }
    _data.pop("bot", None)

    # 2. Поднимаем вебхук
    await bot.set_webhook(
        secret_token=settings.BOT_SECRET, 
        url=f"{settings.WEB_URL.rstrip('/')}/tg-webhook",
        allowed_updates=dp.resolve_used_update_types(),
    )

    try:
        # 3. Триггерим старт
        # Запускаем все on_startup 
        await dp.emit_startup(
            bot=bot, **_data
        )
        
        try:
            # 4. Отдаем 
            # управление FastAPI
            yield
            
        finally:
            # 5. Триггерим события
            # возникающие на остановке
            await dp.emit_shutdown(
                bot=bot, **_data
            )

    finally:
        # 6. Железно удаляем 
        # вебхук при любом исходе
        await bot.delete_webhook(False)





def get_tg_webhook(
    bot: Bot, 
    dp: Dispatcher, 
    settings: Settings
) -> APIRouter:
    """Создает изолированный роутер 
    для приема обновлений от Telegram."""
    
    router = APIRouter(tags=["TG Webhook"])
    x_token = "X-Telegram-Bot-Api-Secret-Token"

    @router.post("/tg-webhook")
    async def tg_webhook(
        request: Request,
        background_tasks: BackgroundTasks,
        secret: str = Header(default="", alias=x_token)
    ) -> dict[str, bool]:
        
        expect = settings.BOT_SECRET
        if not expect or not hmac.compare_digest(secret, expect):
            raise HTTPException(
                status_code=401, 
                detail="Unauthorized"
            )

        try:
            # Парсим данные события 
            # из полученного нами запроса 
            update_data = await request.json()
            update = types.Update.model_validate(
                update_data, context={"bot": bot}
            )
            
        except Exception:
            raise HTTPException(
                status_code=400, 
                detail="Invalid payload"
            ) from None
        
        # Передаем управление 
        # в Aiogram в фоне!
        background_tasks.add_task(
            dp.feed_update, 
            bot, update
        )
        
        return {"ok": True}

    return router
