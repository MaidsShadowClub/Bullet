from typing import Optional

from aiogram.filters.callback_data import CallbackData


class NewsCbFactory(CallbackData, prefix="news"):
    action: str
    value: Optional[int]
    # news_type: models.NewsType
    # data: str
