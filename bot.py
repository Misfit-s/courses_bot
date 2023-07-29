import os
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import message_text

token = os.getenv("TELEGRAM_BOT_TOKEN")
allowed_id = os.getenv("ALLOWED_ID")

class Form(StatesGroup):
    user_id = State()

if not token or allowed_id:
    exit("Specify your TELEGRAM_BOT_TOKEN and ALLOWED_ID env variable")

bot = Bot(token=token)
dp = Dispatcher(bot)

conn = sqlite3.connect(os.path.join("courses.db"))
cursor = conn.cursor()

keyboard_start = InlineKeyboardMarkup(row_width=1)

addCourseBtn = InlineKeyboardButton(text='Добавить курс',
                                    url='',
                                    switch_inline_query='',
                                    switch_inline_query_current_chat='',
                                    pay=False,
                                    callback_data='course_add')

deleteCourseBtn = InlineKeyboardButton(text="Удалить курс",
                                       url='',
                                       switch_inline_query='',
                                       switch_inline_query_current_chat='',
                                       pay=False,
                                       callback_data='course_delete')

keyboard_start.add(addCourseBtn, deleteCourseBtn)


@dp.message_handler(commands=['start', 'help'])
async def start_command(message: types.Message):

    tables = []
    courses = {}

    cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND 
                   name!='sqlite_sequence'""")

    for table in cursor.fetchall():
        tables += table

    for i in tables:
        cursor.execute(f"""SELECT name FROM {i}""")
        courses[i] = cursor.fetchall()

    if message.from_user.id == int(allowed_id):

        await message.answer(text=f'{message_text.START_TEXT_ALLOWED}\
{courses}',
                             reply_markup=keyboard_start)

    else:

        await message.answer(text=message_text.START_TEXT_NOT_ALLOWED)


@dp.callback_query_handler()
async def button_proccess(call: types.CallbackQuery):

    if call.data == "course_add":

        await bot.send_message(text="Вы нажали кнопку добавления события",
                               chat_id=call.message.chat.id)

    elif call.data == "course_delete":

        await bot.send_message(text="Вы нажали кнопку удаления события",
                               chat_id=call.message.chat.id)

if __name__ == "__main__":
   executor.start_polling(dp, skip_updates=True) 
