import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

import core

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    logging.info(f'[{message.from_user.username}]: start')
    await message.answer(core.get_hello_message())


@dp.message()
async def echo_handler(message: Message) -> None:
    logging.info(_mark_user_action(message, message.text))
    try:
        if _url := _extract_url(message):
            answer, err = core.prepare_answer(_url, message.from_user.username)
            if err:
                await message.reply(err)
                logging.warning(_mark_user_action(message, err))
            else:
                await message.reply(answer)
                logging.info(_mark_user_action(message, answer))
    except Exception as e:
        logging.exception(_mark_user_action(message, str(e)))


def _extract_url(message: Message) -> str | None:
    for entity in message.entities if message.entities else []:
        if entity.type == "url":
            return message.text[entity.offset: entity.offset + entity.length]

    return None


def _mark_user_action(message: Message, action: str) -> str:
    return core.mark_action(message.from_user.username, action)


async def start_polling() -> None:
    telegram_bot_api = Bot(token=core.get_telegram_bot_token(),
                           default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(telegram_bot_api)
