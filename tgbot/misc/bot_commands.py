from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot, config) -> None:
    commands = [
        BotCommand(
            command="start",
            description="Start bot"
        ),
        BotCommand(
            command="help",
            description="Print help message"
        ),
    ]
    await bot.set_my_commands(commands=commands,
                              scope=BotCommandScopeDefault())
