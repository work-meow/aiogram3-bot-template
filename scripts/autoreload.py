import sys
import asyncio

from pathlib import Path
from watchfiles import awatch, Change


CMD = [sys.executable, "-m", "app"]
ROOT = Path(__file__).resolve().parent.parent
WATCH_PATH = ROOT / "app"

ICONS = {
    Change.added: "➕",
    Change.modified: "📝",
    Change.deleted: "➖"
}


async def start_app():
    """Запускает процесс приложения."""
    print(f"\n🚀 {' '.join(CMD)}")
    return await asyncio.create_subprocess_exec(*CMD, cwd=str(ROOT))


async def main():
    # Начальный запуск
    proc = await start_app()

    # Фильтр: watchfiles по умолчанию уже игнорирует .git, .venv и __pycache__
    watch_filter = lambda _, path: path.endswith(".py")

    try:
        async for changes in awatch(WATCH_PATH, watch_filter=watch_filter):
            # Печатаем изменения
            for change, path in changes:
                print(f"{ICONS.get(change, '🔔')}")
                print(f"{Path(path).relative_to(ROOT)}")

            # Перезапуск
            if proc.returncode is None:
                proc.terminate()
                await proc.wait()

            proc = await start_app()

    except asyncio.CancelledError:
        pass

    finally:
        if proc.returncode is None:
            proc.terminate()
            await proc.wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass