from aiogram import Router

from .start import router as start_r


common_router = Router(name="common")
common_router.include_routers(start_r)
