import re

from typing import Union, Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsUTC(BaseFilter):
    async def __call__(self, msg: Message) -> Union[bool, Dict[str, int]]:
        text = msg.text
        if not text:
            return False

        utc = re.match(r"^UTC[+-]?\d{1,2}$", text)
        if utc is None:
            return False

        digit = int(text[4:])
        if not -11 <= digit <= 12:
            return False

        return {"timezone": digit}
