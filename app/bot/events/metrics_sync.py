from loguru import logger
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession
from dishka.integrations.aiogram import FromDishka, inject

from app.metrics import registry, COUNTERS
from app.storage import Metric



@inject
async def load_stats(
    container: FromDishka[AsyncContainer]
) -> None:
    """Восстанавливает метрики 
    из БД в память при старте."""
    
    async with container() as ctx:
        db = await ctx.get(AsyncSession)
        
        # 1. Запрашиваем 
        # сохраненные метрики бота
        items = await Metric.get_by_service(db, "bot")
        
        # 2. Переносим значения 
        # из БД в память Prometheus
        restored = 0
        for item in items:
            
            # 3. Если счетчик существует
            # обновляем его значение
            if cnt := COUNTERS.get(item.name):
                cnt.labels(**item.labels).inc(item.value)
                restored += 1

        logger.debug(
            f"📈 Metrics restored: "
            f"from bd: {restored}"
        )




@inject
async def save_stats(
    container: FromDishka[AsyncContainer]
) -> None:
    """Сбрасывает накопленные 
    метрики из памяти в БД."""
    
    # 1. Формируем список 
    # метрик для сохранения
    records = []
    for f in registry.collect():
        
        # Пропускаем гистограммы
        # (они не хранятся у нас в БД)
        if f.type == "histogram":
            continue

        for s in f.samples:
            lbls = s.labels
            
            # 2. Игнорируем метрики
            # от других микросервисов
            if lbls.get("service") != "bot":
                continue
            
            # 3. Игнорируем системный 
            # мусор (таймстемпы Prometheus)
            if s.name.endswith("_created"):
                continue
                
            # 4. Добавляем 
            # данные в список
            records.append({
                "service": "bot", 
                "value": s.value,
                "name": s.name,
                "labels": lbls
            })
    
    if not records:
        return

    # 5. Открываем сессию и 
    # пакетно сохраняем в БД
    async with container() as ctx:
        db = await ctx.get(AsyncSession)
        await Metric.bulk_upsert(db, records)
        await db.commit()
        
        logger.debug(
            "💾 Metrics dumped: "
            f"{len(records)}"
        )