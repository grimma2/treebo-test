import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import logging

import asyncio

from telethon import TelegramClient
from telethon.sessions import MemorySession


scheduled_note_tasks = set()


async def schedule_note_sending(reminder: str, reminder_time: datetime, user_id: int):
    now = datetime.now(ZoneInfo('Europe/Moscow'))
    reminder_time = reminder_time - timedelta(minutes=10)
    reminder_time = reminder_time.replace(tzinfo=ZoneInfo('Europe/Moscow'))

    logging.info(f'Start task for note: {reminder}, at: {reminder_time}')
    logging.info(f'{reminder_time=}')
    logging.info(f'{now=}')

    if reminder_time > now:
        sleep_time = (reminder_time - now).total_seconds()
        logging.info(f'{sleep_time=}')
        await asyncio.sleep(sleep_time)
    else:
        logging.info('send note right now')

    client = TelegramClient(MemorySession(), api_id=os.environ['API_ID'], api_hash=os.environ['API_HASH'])
    await client.start(bot_token=os.environ['BOT_TOKEN'])

    await client.send_message(entity=user_id, message=reminder)
    await client.disconnect()
