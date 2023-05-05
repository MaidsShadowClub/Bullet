import aiofiles
import logging

from typing import List

from jinja2 import Template

from aiogram import types
from aiogram import Router
from aiogram.filters import Command
from aiogram.types.inline_query import InlineQuery
from aiogram.types.inline_query_result_article import InlineQueryResultArticle
from aiogram.types.input_text_message_content import InputTextMessageContent

from sqlalchemy import select


import models
from tgbot.middlewares.get_cve import CVEMessageMiddleware


logger = logging.getLogger(__name__)

get_cve_router = Router()
get_cve_router.message.middleware(CVEMessageMiddleware())
get_cve_router.inline_query.middleware(CVEMessageMiddleware())


@get_cve_router.message(Command("id"))
async def get_cve_msg(msg: types.Message, cves: List[str]) -> None:
    if cves == []:
        await msg.answer("Didn't find any identificator")
        return

    engine = models.db_async_connect()
    try:
        async with engine.connect() as conn:
            ans = await _get_cve_msg(cves, conn)
    except Exception as e:
        ans = "Internal error"
        logger.error(e)
    finally:
        await engine.dispose()

    if ans == "":
        ans = "There is no information in a database"

    await msg.answer(ans)


@get_cve_router.inline_query()
async def get_cve_inline(inline_query: InlineQuery, cves: List[str]):
    if cves == []:
        return

    engine = models.db_async_connect()
    try:
        async with engine.connect() as conn:
            ans = await _get_cve_msg(cves, conn)
    except Exception as e:
        ans = "Internal error"
        logger.error(e)
    finally:
        await engine.dispose()

    if ans == "":
        ans = "There is no information in a database"

    results = [
        InlineQueryResultArticle(
            id="GetCVEInline",
            title="Search info in security bulletins about",
            description=cves[0],
            input_message_content=InputTextMessageContent(
                message_text=ans
            )
        )
    ]
    await inline_query.answer(results, cache_time=5)  # 86400)


async def _get_cve_msg(cve_names, conn) -> str:
    async with aiofiles.open("templates/info_about_cve.j2") as file:
        template_string = await file.read()
    template = Template(template_string)

    cve_name = cve_names[0]  # take first matched by regex

    ret = ""
    cves = await conn.execute(
        select(models.CVE)
        .where(models.CVE.name == cve_name)
    )
    for cve in cves:
        cve_bull_vend_row = await conn.execute(
            select(
                models.Bulletin,
                models.CVEInfo,
                models.Vendor,
            )
            .select_from(models.CVE)
            .join(models.Bulletin)
            .join(models.CVEInfo)
            .join(models.Vendor, models.Vendor.id == models.Bulletin.vendor_id)
            .where(models.CVE.id == cve.id)
        )
        cve_bull_vend = cve_bull_vend_row.first()
        ret += template.render(
            cve=cve.name,
            vendor=cve_bull_vend.name,
            bulletin=cve_bull_vend.title,
            header=cve_bull_vend.header,
            description=cve_bull_vend.description,
            reported=cve_bull_vend.reported,
            patch=cve_bull_vend.patch,
            links=cve_bull_vend.links,
            affected=cve_bull_vend.affected,
            severity=cve_bull_vend.severity,
            weakness=cve_bull_vend.weakness
        )
        ret += "```------------------```"

    return ret
