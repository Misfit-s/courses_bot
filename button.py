from aiogram.types import InlineKeyboardButton


def create_button(text, callback):
    button = InlineKeyboardButton(
            text=text,
            pay=False,
            url='',
            callback_data=callback,
            switch_inline_query='',
            switch_inline_query_current_chat=''
            )
    return button
