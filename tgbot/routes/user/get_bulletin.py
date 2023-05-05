import aiofiles
import logging

from jinja2 import Template

from aiogram import types
from aiogram import Router
from aiogram.filters import Command
from sqlalchemy import select

from tgbot.keyboards.inline import get_vendor_kb

import models

logger = logging.getLogger(__name__)

get_bulletin_router = Router()


@get_bulletin_router.message(Command("bull"))
async def get_bulletin(msg: types.Message):
    kb = None
    engine = models.db_async_connect()
    try:
        async with engine.connect() as conn:
            vendors = await conn.execute(
                select(models.Vendor)
            )
            kb = get_vendor_kb(vendors.all())
            ans = "Choose vendor of bulletins"
    except Exception as e:
        ans = "Internal error"
        logger.error(e)
    finally:
        await engine.dispose()
    await msg.answer(ans, reply_markup=kb)


@get_bulletin_router.callback_query()
async def get_bulletin_cb(callback: types.CallbackQuery):
    text = callback.data
    await callback.message.answer("You choose " + text)

    await callback.answer()
