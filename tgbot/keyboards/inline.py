# from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .callback_data import NewsCbFactory


def get_vendor_kb(vendors) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for vendor in vendors:
        keyboard.add(
            InlineKeyboardButton(
                text=vendor.name,
                callback_data=NewsCbFactory(
                    action="change", value=-2
                    # news_type=models.NewsType.cve_vendor,
                    # data=name
                )
            )
        )
    keyboard.adjust(2)

    return keyboard.as_markup(selective=True)
