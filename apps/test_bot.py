from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
load_dotenv('.env')

from telethon import TelegramClient
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram import types
from aiogram.fsm.context import FSMContext

from .handlers import start_command, name_received
from .notes_scheduler import schedule_note_sending


@pytest.mark.asyncio
async def test_start_command():
    # Создайте mock объекты
    message = MagicMock(spec=types.Message)
    state = AsyncMock(spec=FSMContext)
    repository = MagicMock()
    repository.get_username_if_exists = AsyncMock(return_value=None)  # Или укажите mock-значение, если ожидаете имя

    # Установите значения для mock объектов
    message.from_user = AsyncMock()
    message.from_user.id = 123
    message.from_user.first_name = "TestUser"
    
    # Вызовите функцию
    await start_command(message, state)

    # Проверьте, что методы были вызваны
    repository.init_db.assert_awaited()
    message.answer.assert_called_with(
        "Привет TestUser! Давайте зарегистрируемся. Введите ваше имя.",
        reply_markup=MagicMock()
    )


@pytest.mark.asyncio
async def test_name_received():
    message = AsyncMock(spec=types.Message)
    state = AsyncMock(spec=FSMContext)

    message.from_user = AsyncMock()
    message.answer = AsyncMock()
    message.from_user.id = 123
    message.from_user.first_name = "TestUser"
    message.text = "TestName"

    await name_received(message, state)

    state.update_data.assert_awaited_with(name="TestName")
    message.answer.assert_awaited_with(
        "Введите ваш email.", reply_markup=types.ReplyKeyboardRemove()
    )


@pytest.mark.asyncio
async def test_schedule_note_sending():
    reminder = "Test reminder"
    reminder_time = datetime(2024, 8, 4, 18, 20)
    user_id = 123
    
    # Подготовка mock объекта TelegramClient
    mock_client = AsyncMock(spec=TelegramClient)
    
    # Используйте правильный путь для подмены
    with patch('apps.notes_scheduler.TelegramClient', return_value=mock_client):
        await schedule_note_sending(reminder, reminder_time, user_id)

        # Проверьте, что функции отправки сообщения и отключения клиента были вызваны
        mock_client.send_message.assert_awaited_with(entity=user_id, message=reminder)
        mock_client.disconnect.assert_awaited()


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    monkeypatch.setenv('API_ID', 'your_api_id')
    monkeypatch.setenv('API_HASH', 'your_api_hash')
    monkeypatch.setenv('BOT_TOKEN', 'your_bot_token')
