import os
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.dispatcher.filters import state
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext, storage
import message_text

token = os.getenv("TELEGRAM_BOT_TOKEN") # Telegram token
allowed_id = os.getenv("ALLOWED_ID") # Telegram user token

class Form(StatesGroup):
    name = State()
    materials = State()
    done = State()

if not token or not allowed_id:
    exit("Specify your TELEGRAM_BOT_TOKEN and ALLOWED_ID env variable")

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

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

        msg = await message.answer(text=f'{message_text.START_TEXT_ALLOWED}\
{courses}',
                             reply_markup=keyboard_start)

    else:

        await message.answer(text=message_text.START_TEXT_NOT_ALLOWED)


@dp.callback_query_handler()
async def button_proccess(call: types.CallbackQuery):

    # Course add
    if call.data == "course_add":

        await Form.name.set()
        await bot.edit_message_text(message_id=call.message.message_id,
                                    text=message_text.ADD_TEXT_NAME,
                                    chat_id=call.message.chat.id)


        @dp.message_handler(state=Form.name)
        async def proccess_name(message: types.Message, state: FSMContext):

            async with state.proxy() as data:
                data['name'] = message.text

            await Form.materials.set()
            await bot.send_message(text=message_text.ADD_TEXT_MATERIALS,
                                   chat_id=call.message.chat.id)

        @dp.message_handler(state=Form.materials)
        async def proccess_materials(message: types.Message,
                                     state: FSMContext):
            async with state.proxy() as data:
                data['materials'] = message.text

            await Form.done.set()
            await bot.send_message(text=message_text.ADD_TEXT_DONE,
                                   chat_id=call.message.chat.id)


        @dp.message_handler(state=Form.done)
        async def proccess_done(message: types.Message, state: FSMContext):

            async with state.proxy() as data:
                data['done'] = message.text

            await state.finish()

            await bot.send_message(text=message_text.ADD_TEXT_COMPLETE,
                                   chat_id=call.message.chat.id)
            
            cursor.execute(f'INSERT INTO')
            # TODO: Сделать указание платформы для добавления новых курсов.
            # Можно попробовать сделать цикл добавления кнопок кливиатуры
            # С платформами.


    # Course delete
    elif call.data == "course_delete":

        await bot.send_message(text="Вы нажали кнопку удаления события",
                               chat_id=call.message.chat.id)

if __name__ == "__main__":
   executor.start_polling(dp, skip_updates=True) 
