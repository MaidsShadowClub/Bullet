import re
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

from sqlalchemy import select, or_


import models

logger = logging.getLogger(__name__)

find_info_router = Router()


@find_info_router.message(Command("find"))
async def find_info_msg(msg: types.Message) -> None:
    to_find = filter_symbols(msg.text)
    if to_find == "":
        await msg.answer("Nothing to find")
        return
    to_find = "%"+to_find+"%"  # mysql regex to find all

    engine = models.db_async_connect()
    try:
        async with engine.connect() as conn:
            ans = await _find_info_msg(to_find, conn)
    except Exception as e:
        ans = "Internal error"
        logger.error(e)
    finally:
        await engine.dispose()

    if ans == []:
        ans = ["There is no information in a database"]

    for a in ans:
        a = re.sub(r"-", "\\-", a)
        a = re.sub(r"_", "\\_", a)
        a = re.sub(r"\+", "\\+", a)
        a = re.sub(r"\.", "\\.", a)
        a = re.sub(r"\(", "\\(", a)
        a = re.sub(r"\)", "\\)", a)
        print(a)
        await msg.answer(a)


def filter_symbols(value):
    value = re.sub(r"^.*\s", "", value)  # to delete command
    return re.sub("[^A-Za-z0-9-_ ]", "", value)


async def _find_info_msg(to_find, conn) -> str:
    async with aiofiles.open("templates/info_about_cve.j2") as file:
        template_string = await file.read()
    template = Template(template_string)

    ret = []
    cve_infos = await conn.execute(
        select(
            models.CVEInfo,
            models.Bulletin,
            models.Vendor
        )
        .select_from(models.CVEInfo)
        .join(models.Bulletin)
        .join(models.Vendor, models.Vendor.id == models.Bulletin.vendor_id)
        .where(
            or_(
                models.CVEInfo.header.ilike(to_find),
                models.CVEInfo.description.ilike(to_find)
            )
        )
    )
    for cve_info in cve_infos.all():
        cves = await conn.execute(
            select(models.CVE)
            .where(models.CVE.cve_info_id == cve_info.id)
        )
        cves_name = " ".join([cve.name for cve in cves.all()])
        ret.append(template.render(
            cve=cves_name,
            vendor=cve_info.name,
            bulletin=cve_info.title,
            header=cve_info.header,
            description=cve_info.description,
            reported=cve_info.reported,
            patch=cve_info.patch,
            links=cve_info.links,
            affected=cve_info.affected,
            severity=cve_info.severity,
            weakness=cve_info.weakness
        ))

    return ret
