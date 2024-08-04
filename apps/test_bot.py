from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
load_dotenv('.env')

import pytest
from unittest.mock import AsyncMock
from aiogram import types
from aiogram.fsm.context import FSMContext

from .handlers import name_received


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
