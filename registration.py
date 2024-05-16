from telebot import types
from datetime import datetime

def create_register_form():
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    register_button = types.InlineKeyboardButton("Register", callback_data="send_contact")
    inline_keyboard.add(register_button)
    
    return inline_keyboard


def get_current_date():
    # Get the current date
    current_date = datetime.now()

    # Format the date as "dd.mm.yy" and return as string
    formatted_date = current_date.strftime("%d.%m.%y")

    return formatted_date