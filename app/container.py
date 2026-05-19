import orjson
import aiohttp

from aiogram import Bot
from loguru import logger
from typing import Any, NewType
from aiogram.enums import ParseMode
from aiohttp_socks import ProxyConnector
from collections.abc import AsyncIterable
from dishka import make_async_container, provide
from dishka import AsyncContainer, Provider, Scope
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.storage import session_factory, engine, ping_database
from app.services import QueueManager, QueueService
from app.settings import get_settings, Settings



# --- Хелперы ---
def orjson_dumps(obj: Any) -> str:
    """Обертка для быстрой сериализации JSON."""
    return orjson.dumps(obj).decode()



# --- Уникальные типы для DI ---
DirectSession = NewType("DirectSession", aiohttp.ClientSession)
ProxySession = NewType("ProxySession", aiohttp.ClientSession)



class AppProvider(Provider):
    scope = Scope.APP

    async def _clear(self, instance: Any) -> None:
        """Универсальное завершение работы."""

        for method in ("close", "stop", "dispose"):
            if closer := getattr(instance, method, None):
                logger.debug(f"♻️ Shutdown: {instance.__class__.__name__}")
                await closer()
                break


    # --- Клиенты HTTP ---
    @provide
    async def direct_session(
        self
    ) -> AsyncIterable[DirectSession]:
        
        connector = aiohttp.TCPConnector(
            limit=100,
            keepalive_timeout=60,
            enable_cleanup_closed=True,
            use_dns_cache=True,
        )

        session = aiohttp.ClientSession(
            connector=connector,
            json_serialize=orjson_dumps
        )

        yield DirectSession(session)
        await self._clear(session)



    @provide
    async def proxy_session(
        self, 
        settings: Settings
    ) -> AsyncIterable[ProxySession]:
        
        connector_kwargs = {
            "limit": 100,
            "keepalive_timeout": 60,
            "enable_cleanup_closed": True,
            "use_dns_cache": True,
        }

        if settings.PROXY_URL:
            connector = ProxyConnector.from_url(
                settings.PROXY_URL,
                **connector_kwargs
            )

        else:
            logger.warning(
                "Proxy не задан, ProxySession "
                "работает напрямую!"
            )

            connector = aiohttp.TCPConnector(
                **connector_kwargs
            )

        session = aiohttp.ClientSession(
            connector=connector,
            json_serialize=orjson_dumps,
        )

        yield ProxySession(session)
        await self._clear(session)



    # --- Сессия Бота ---
    @provide
    async def bot_session(
        self, 
        settings: Settings
    ) -> AsyncIterable[AiohttpSession]:
        
        proxy = (
            settings.PROXY_URL
            if settings.BOT_PROXY
            else None
        )

        session = AiohttpSession(
            json_loads=orjson.loads,
            json_dumps=orjson_dumps,
            proxy=proxy
        )

        yield session
        await self._clear(session)



    @provide
    async def bot(
        self, 
        session: AiohttpSession, 
        settings: Settings
    ) -> Bot:
        
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
            logger.debug("🗄 New session bd")
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
        return get_settings()




async def init_container() -> AsyncContainer:
    """Сборка DI-контейнера и прогрев критических сервисов."""

    logger.info("🛠 Сборка DI-контейнера...")
    container = make_async_container(AppProvider())
    await container.get(AsyncEngine)
    return container