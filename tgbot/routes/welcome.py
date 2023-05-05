import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from sqlalchemy import insert, select

import models

welcome_router = Router()
logger = logging.getLogger(__name__)


@welcome_router.message(CommandStart())
async def on_start_command(msg: Message) -> None:
    engine = models.db_async_connect()
    await models.async_create_table(engine)
    try:
        usr = msg.from_user
        async with engine.connect() as conn:
            exists = await conn.execute(
                select(models.User)
                .where(models.User.tg_id == usr.id)
            )
            if exists.first():
                return
            await conn.execute(
                insert(models.User)
                .values(tg_id=usr.id)
            )
            await conn.commit()

        logger.info("New user %s %s(%s) - %d" %
                    (usr.first_name, usr.last_name, usr.username, usr.id))
        ans = (
            "Hello comrade! Let's set up something - press links below\n" +
            "/news\\_time - set up timezone (must)\n" +
            "/news\\_cve - set up CVEs news\n" +
            "/news\\_article - set up articles news\n"
            # "/news\\_conference - set up conferences news"
        )
    except Exception as e:
        ans = "Internal error"
        logger.error(e)
    finally:
        await engine.dispose()

    await msg.answer(ans)


# @welcome_router.message(Command(commands="help"))
# async def on_help_command(msg: Message) -> None:
#     ans = (
#         "/id - to look for vulns by id\n" +
#         # "/find - to look for vulns by title or description\n" +
#         "/news_time - change timezone to receive a message in 13:37\n"
#         # "/news_cve - set up your desired newsletter of cves\n" +
#         # "/news_article - set up your desired newsletter of articles\n" +
#         # "/news_conference - set up your desired newsletter of conferences"
#     )
#
#     await msg.answer(ans)
