from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.types.inline_query import InlineQuery

from items import get_cve_names


class CVEMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | InlineQuery,
        data: Dict[str, Any]
    ) -> Any:
        data["cves"] = []
        text = None
        if getattr(event, "text", None):
            text = event.text
        if getattr(event, "query", None):
            text = event.query
        if text is None:
            return await handler(event, data)

        cves = get_cve_names(text.upper())
        data["cves"] = cves

        return await handler(event, data)
