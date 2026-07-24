from aiogram import Router

from .start import router as start_r
from .album import router as album_r
from .rich import router as rich_r


example_router = Router(name="example")
example_router.include_routers(start_r)
example_router.include_routers(album_r)
example_router.include_routers(rich_r)