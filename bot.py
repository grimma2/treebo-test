import logging
import os

from dotenv import load_dotenv
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from apps.handlers import router


load_dotenv('.env')


logging.basicConfig(
    handlers=(logging.StreamHandler(),),
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)


async def main():
    bot = Bot(token=os.environ['BOT_TOKEN'], default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
