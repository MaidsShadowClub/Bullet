from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_UTC_kb() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    for i in range(-11, 12+1):
        keyboard.add(KeyboardButton(text=f"UTC{i:+}"))
    keyboard.adjust(4)

    return keyboard.as_markup(resize_keyboard=True)
