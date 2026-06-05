from fastapi import FastAPI
from dishka import AsyncContainer
from uvicorn import Config, Server
from fastapi.middleware.cors import CORSMiddleware
from dishka.integrations.fastapi import setup_dishka

from .exceptions import setup_exceptions
from .routers import setup_routers
from app.settings import Settings



def create_app(
    container: AsyncContainer
) -> FastAPI:
    """Собирает FastAPI 
    приложение."""

    app = FastAPI(
        version="1.0",
        title="Service API",
        description="Service API",
        swagger_ui_parameters={
            "displayRequestDuration": True,
            "persistAuthorization": True,
        },
    )
    
    # 2. Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )
    
    # 3. Прокидываем контейнер
    setup_dishka(container, app)
    
    # 4. Обработчики ошибок
    setup_exceptions(app)

    # 5. Добавляем роутеры
    setup_routers(app)

    return app



async def run_server(
    app: FastAPI,
    settings: Settings
) -> None:
    """Запуск Uvicorn
    сервера."""

    config = Config(
        app=app,
        loop="uvloop",
        http="httptools",
        host=settings.WEB_HOST,
        port=settings.WEB_PORT,
        log_level=settings.LOG_LEVEL.lower(),
        timeout_graceful_shutdown=60,
        access_log=True,
        reload=False,
    )
    
    server = Server(config)
    await server.serve()