from fastapi import FastAPI

# from .v1 import v1_router
# from .v2 import v2_router


def setup_routers(app: FastAPI) -> None:
    """Устанавливаем все роутеры."""

    # 1. Корневой эндпоинт
    @app.get("/", tags=["Root"])
    async def root() -> dict[str, str]:
        return {"message": "Bot API v1.0"}


    # 2. Подключаем роутеры
    # app.include_router(v1_router)
    # app.include_router(v2_router)


    # 3. Проверка здоровья
    @app.get("/health", tags=["Health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}