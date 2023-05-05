from aiogram import Dispatcher, Router

from .welcome import welcome_router
from .user.get_cve import get_cve_router
from .user.find_info import find_info_router
from .user.set_up_news import set_up_news_router
from .user.get_bulletin import get_bulletin_router


def register_all_routes(dp: Dispatcher, config) -> None:
    master_router = Router()
    dp.include_router(master_router)

    master_router.include_router(welcome_router)
    master_router.include_router(get_cve_router)
    master_router.include_router(find_info_router)
    master_router.include_router(set_up_news_router)
    master_router.include_router(get_bulletin_router)
