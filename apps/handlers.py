import asyncio

from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from .repository import NotesRepository
from .notes_scheduler import schedule_note_sending, scheduled_note_tasks

import logging
from datetime import datetime


repository = NotesRepository()
router = Router()


class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_email = State()


class NoteState(StatesGroup):
    waiting_for_text = State()
    waiting_for_time = State()


@router.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    await repository.init_db()

    logging.info("Start command received from user: %s", message.from_user.id)
    first_name = await repository.get_username_if_exists(telegram_id=message.from_user.id)
    
    if first_name:
        await message.answer(f"Здравствуйте, {first_name}!")
        logging.info("User %s already registered", message.from_user.id)
    else:
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text=f"Оставить '{message.from_user.first_name}'")]
            ],
            resize_keyboard=True
        )

        await message.answer(f"Привет {message.from_user.first_name}! Давайте зарегистрируемся. Введите ваше имя.", reply_markup=keyboard)
        await state.set_state(Registration.waiting_for_name)
        logging.info("Starting registration for user %s", message.from_user.id)


@router.message(Registration.waiting_for_name)
async def name_received(message: types.Message, state: FSMContext):
    if message.text == f"Оставить '{message.from_user.first_name}'":
        await state.update_data(name=message.from_user.first_name)
    else:
        await state.update_data(name=message.text)

    await message.answer("Введите ваш email.", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Registration.waiting_for_email)
    logging.info("Name received from user %s: %s", message.from_user.id, message.text)


@router.message(Registration.waiting_for_email)
async def email_received(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    await repository.create_user(
        telegram_id=message.from_user.id, 
        name=user_data['name'], 
        email=message.text
    )

    await state.clear()
    await message.answer("Регистрация завершена!")
    logging.info("Email received and user %s registered: %s", message.from_user.id, message.text)


@router.message(Command("addnote"))
async def add_note_command(message: types.Message, state: FSMContext):
    await state.set_state(NoteState.waiting_for_text)
    await message.answer("Введите текст заметки:")
    logging.info("User %s started adding a note", message.from_user.id)


@router.message(NoteState.waiting_for_text)
async def note_received(message: types.Message, state: FSMContext):
    await state.update_data(note=message.text)
    await state.set_state(NoteState.waiting_for_time)
    await message.answer("Введите время напоминания в формате день.месяц.год часы:минуты")
    logging.info("Note text received from user %s: %s", message.from_user.id, message.text)


@router.message(NoteState.waiting_for_time)
async def time_received(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    try:
        reminder_time = datetime.strptime(message.text, '%d.%m.%Y %H:%M')
    except ValueError:
        logging.info(f'incorent data: {message.text}')
        await message.answer('Неверный формат даты :(')
        await message.answer("Введите время напоминания в формате день.месяц.год часы:минуты")
        return

    await repository.add_note(
        user_id=message.from_user.id, 
        text=user_data['note'], 
        reminder_time=reminder_time
    )

    note_task = asyncio.create_task(
        schedule_note_sending(
            user_id=message.from_user.id,
            reminder=user_data['note'],
            reminder_time=reminder_time,
        )
    )

    scheduled_note_tasks.add(note_task)
    note_task.add_done_callback(scheduled_note_tasks.discard)

    await state.clear()
    await message.answer("Заметка добавлена!")
    logging.info("Reminder time received and note added for user %s: %s", message.from_user.id, message.text)


@router.message(Command('mynotes'))
async def view_notes_command(message: types.Message):
    notes = await repository.get_notes(message.from_user.id)
    response = "\n".join([f"{note['id']}: {note['text']} - {note['reminder_time']}" for note in notes])
    await message.answer(response or "У вас нет заметок.")
    logging.info("User %s requested their notes", message.from_user.id)
