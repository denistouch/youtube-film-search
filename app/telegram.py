import log
import uuid

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

import core

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    log.info(f'[{message.from_user.username}]: start')
    await message.answer(core.get_hello_message())


@dp.message()
async def echo_handler(message: Message) -> None:
    _id = str(uuid.uuid4())
    try:
        log.info(_mark_user_action(message, 'send'), _id, message)
        if _url := _extract_url(message):
            answer, err = core.prepare_answer(_url, message.from_user.username, _id, core.get_provider(message.from_user.id))
            if err:
                await message.reply(err)
                log.warning(_mark_user_action(message, err), _id)
            else:
                await message.reply(answer)
                log.info(_mark_user_action(message, answer), _id)
    except Exception as e:
        log.exception(e, _id, message)


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
    dp.shutdown.register(core.shutdown)
    await dp.start_polling(telegram_bot_api)

async def stop_polling() -> None:
    await dp.stop_polling()
