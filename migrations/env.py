import asyncio

from alembic import context
from sqlalchemy import pool
from logging.config import fileConfig
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.settings import get_settings
import app.storage.models


config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


settings = get_settings()
db_url = str(settings.DATABASE_URL)
target_metadata = app.storage.models.BaseModel.metadata



def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме."""
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        dialect_opts={"paramstyle": "named"},
        literal_binds=True,
    )

    with context.begin_transaction():
        context.run_migrations()



def do_run_migrations(connection: Connection) -> None:
    """Выполнение миграций на физическом коннекте."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_server_default=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()



async def run_async_migrations() -> None:
    """Асинхронный запуск миграций."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = db_url

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()



def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме."""
    asyncio.run(run_async_migrations())



if context.is_offline_mode():
    run_migrations_offline()
else: run_migrations_online()