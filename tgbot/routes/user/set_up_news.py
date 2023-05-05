import logging


from aiogram import Router
from aiogram import types
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from sqlalchemy import update, select

from tgbot.filters.set_up_news import IsUTC
from tgbot.keyboards.inline import get_vendor_kb
from tgbot.keyboards.reply import get_UTC_kb

import models


set_up_news_router = Router()
logger = logging.getLogger(__name__)


# TODO: add method to delete elements from my_news

@set_up_news_router.message(Command("my_news"))
async def show_settings(msg: types.Message) -> None:
    engine = models.db_async_connect()
    try:
        async with engine.connect() as conn:
            usr_row = await conn.execute(
                select(models.User)
                .where(models.User.tg_id == msg.from_user.id)
            )
            usr = usr_row.first()
            if usr is None:
                ans = "You doesn't exist in database. Type /start"
            else:
                ans = (
                    f"*UTC:* {usr.timezone}\n" +
                    f"*CVEs:* {1}\n" +
                    f"*Articles:* {1}\n" +
                    f"*Conferences:* {1}"
                )
    except Exception as e:
        ans = "Internal error"
        logger.error(e)
    finally:
        await engine.dispose()

    await msg.answer(ans)


@set_up_news_router.message(Command("news_time"))
async def choose_news_time(msg: types.Message) -> None:
    ans = ("This bot is so elite " +
           "that it only sends bulletins at 13:37, " +
           "so choose your timezone")
    kb = get_UTC_kb()
    await msg.answer(ans, reply_markup=kb)


@set_up_news_router.message(Command("news_cve"))
async def choose_news_cve(msg: types.Message) -> None:
    kb = None
    engine = models.db_async_connect()
    try:
        async with engine.connect() as conn:
            vendors = await conn.execute(
                select(models.Vendor)
            )
            kb = get_vendor_kb(vendors.all())
            ans = "Choose security bulletins what you want receive"
    except Exception as e:
        ans = "Internal error"
        logger.error(e)
    finally:
        await engine.dispose()
    await msg.answer(ans, reply_markup=kb)


@set_up_news_router.message(IsUTC())
async def set_news_time(msg: types.Message, timezone: int) -> None:
    engine = models.db_async_connect()
    try:
        async with engine.connect() as conn:
            ans = await _set_news_time(timezone, conn, msg.from_user)
    except Exception as e:
        ans = "Internal error"
        logger.error(e)
    finally:
        await engine.dispose()

    await msg.answer(ans, reply_markup=types.ReplyKeyboardRemove())


async def _set_news_time(timezone: int, conn, usr) -> str:
    exists = await conn.execute(
        select(models.User)
        .where(models.User.tg_id == usr.id)
    )
    if exists.first() is None:
        return "There is no info in database. Type /start"

    await conn.execute(
        update(models.User)
        .values(timezone=timezone)
    )
    await conn.commit()
    return "Successfully set timezone"
