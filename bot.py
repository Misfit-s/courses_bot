import os
import sqlite3

from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, chat
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

import message_text
import button

token = os.getenv("TELEGRAM_BOT_TOKEN")  # Telegram token
allowed_id = os.getenv("ALLOWED_ID")  # Telegram user token


class Form(StatesGroup):
    """ """
    name = State()
    materials = State()
    done = State()
    platform = State()


if not token or not allowed_id:
    exit("Specify your TELEGRAM_BOT_TOKEN and ALLOWED_ID env variable")

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

conn = sqlite3.connect(os.path.join("courses.db"))
cursor = conn.cursor()

keyboard_start = InlineKeyboardMarkup(row_width=1)


@dp.message_handler(commands=["start", "help"])
async def start_command(message: types.Message):
    tables = []
    courses = {}

    cursor.execute(
        """SELECT name FROM sqlite_master WHERE type='table' AND
                   name!='sqlite_sequence'"""
    )

    for table in cursor.fetchall():
        tables += table

    for table in tables:
        keyboard_start.add(button.create_button(table, f"{table}_btn"))

    for i in tables:
        cursor.execute(f"""SELECT name FROM {i}""")
        courses[i] = cursor.fetchall()

    if message.from_user.id == int(allowed_id):
        await message.answer(
            text=f"{message_text.START_ALLOWED}{courses}",
            reply_markup=keyboard_start
        )

    else:
        await message.answer(text=message_text.START_TEXT_NOT_ALLOWED)


@dp.callback_query_handler(lambda c: c.data.endswith("_btn"))
async def button_platform_proccess(call: types.CallbackQuery,
                                   state: FSMContext):

    platform = call.data.replace("_btn", "")
    await state.update_data(platform=platform)

    platform_keyboard = InlineKeyboardMarkup()

    platform_keyboard.add(
            button.create_button("Добавить курс", "course_add"),
            button.create_button("Удалить курс", "course_del")
            )

    await bot.send_message(
            text="test",
            chat_id=call.message.chat.id,
            reply_markup=platform_keyboard,
            )


@dp.callback_query_handler(lambda c: c.data.startswith("course_"))
async def button_course_proccess(call: types.CallbackQuery,
                                 state: FSMContext):
    if call.data == "course_add":
        print("Добавить курс")

    elif call.data == "course_del":
        print("Удалить курс")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
