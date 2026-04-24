import orjson

from typing import Any
from aiogram import Bot
from loguru import logger
from aiogram.enums import ParseMode
from collections.abc import AsyncIterable
from dishka import make_async_container, provide
from dishka import AsyncContainer, Provider, Scope
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.storage import session_factory, engine, ping_database
from app.services import QueueManager, QueueService
from app.settings import get_settings, Settings


class AppProvider(Provider):
    scope = Scope.APP

    async def _clear(self, instance: Any) -> None:
        """Универсальное завершение работы."""
        for method in ("close", "stop", "dispose"):
            if closer := getattr(instance, method, None):
                logger.debug(f"♻️ Shutdown: {instance.__class__.__name__}")
                await closer()
                break

    # --- Сессия Aiohttp ---

    @provide
    async def aiohttp_session(self) -> AsyncIterable[AiohttpSession]:
        session = AiohttpSession(
            json_loads=orjson.loads,
            json_dumps=lambda obj: orjson.dumps(obj).decode()
        )
        yield session
        await self._clear(session)

    # --- Сессия Бота ---

    @provide
    async def bot(self, session: AiohttpSession, settings: Settings) -> Bot:
        """Инжектит готового бота в любые сервисы."""
        return Bot(
            session=session,
            token=settings.BOT_TOKEN,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML,
                link_preview_is_disabled=True,
                allow_sending_without_reply=True
            )
        )

    # --- База данных ---

    @provide
    async def db_engine(self) -> AsyncIterable[AsyncEngine]:
        await ping_database()
        yield engine
        await self._clear(engine)


    @provide(scope=Scope.REQUEST)
    async def db_session(self) -> AsyncIterable[AsyncSession]:
        async with session_factory() as session:
            yield session

    # --- Сервис очереди ---

    @provide
    async def queue(self) -> AsyncIterable[QueueService]:
        service = QueueService(QueueManager(workers=50))
        yield service
        await self._clear(service)

    # --- Настройки ---

    @provide
    def app_settings(self) -> Settings:
        """Отдаем настройки в DI."""
        return get_settings()



async def init_container() -> AsyncContainer:
    """Сборка DI-контейнера и прогрев критических узлов."""
    logger.info("🛠 Сборка DI-контейнера...")
    container = make_async_container(AppProvider())
    await container.get(AsyncEngine)
    return container