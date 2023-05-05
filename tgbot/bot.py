import logging

from aiogram import Bot, Dispatcher
from scrapy.utils.project import get_project_settings

from .misc.bot_commands import set_commands
from .routes import register_all_routes

logger = logging.getLogger(__name__)


async def main():
    config = get_project_settings()
    bot = Bot(token=config["API_TOKEN"], parse_mode="MarkdownV2")

    dp = Dispatcher()

    register_all_routes(dp, config)
    await set_commands(bot, config)
    try:
        logger.info('Starting bot')
        await bot.get_updates(offset=-1)
        await dp.start_polling(bot,
                               allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
