import os
import logging
from datetime import datetime

import asyncpg


class NotesRepository:

    async def init_db(self) -> None:
        conn = await asyncpg.connect(os.environ['DATABASE_URL'])
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT,
                email TEXT,
                telegram_id INTEGER UNIQUE
            )
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(telegram_id),
                text TEXT,
                reminder_time TIMESTAMP
            )
        ''')
        await conn.close()

        logging.info("Database initialized")

    async def get_username_if_exists(self, telegram_id: int) -> bool:
        conn = await asyncpg.connect(os.environ['DATABASE_URL'])

        first_name = await conn.fetchval('SELECT name FROM users WHERE telegram_id = $1', telegram_id)
        if first_name:
            logging.info("User %s already exists", telegram_id)
            await conn.close()
            return first_name

    async def create_user(self, telegram_id: int, name: str, email: str) -> None:
        conn = await asyncpg.connect(os.environ['DATABASE_URL'])

        await conn.execute(
            'INSERT INTO users (name, email, telegram_id) VALUES ($1, $2, $3)', name, email, telegram_id
        )
        await conn.close()
        logging.info("User %s created with name: %s and email: %s", telegram_id, name, email)

    async def add_note(self, user_id: int, text: str, reminder_time: datetime) -> None:
        conn = await asyncpg.connect(os.environ['DATABASE_URL'])
        users = await conn.fetch('SELECT * FROM users;')
        for user in users:
            logging.info(user)

        await conn.execute('INSERT INTO notes (user_id, text, reminder_time) VALUES ($1, $2, $3)', user_id, text, reminder_time)
        await conn.close( )
        logging.info("Note added for user %s: %s at %s", user_id, text, reminder_time)

    async def get_notes(self, user_id: int) -> None:
        conn = await asyncpg.connect(os.environ['DATABASE_URL'])
        notes = await conn.fetch('SELECT * FROM notes WHERE user_id = $1 ORDER BY reminder_time', user_id)
        logging.info("Notes retrieved for user %s", user_id)
        await conn.close()
        
        return notes
