import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import calendar
from datetime import datetime

def generate_inline_calendar(year = datetime.now().year, month = datetime.now().month):
    keyboard = InlineKeyboardMarkup(row_width=7)
    month_name = calendar.month_name[month]
    next_month = calendar.month_name[month + 1]
    keyboard.add(InlineKeyboardButton(f"<< {month_name} {year}", callback_data=f'prevmonth_{month}_{year}'))
    keyboard = InlineKeyboardMarkup(row_width=7)
    month_name = calendar.month_name[month]
    keyboard.add(InlineKeyboardButton(f"<< {month_name} {year}", callback_data=f'prevmonth_{month}_{year}'))

    days_of_week = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
    keyboard.add(*[InlineKeyboardButton(day, callback_data='ignore') for day in days_of_week])
    month_days = calendar.monthcalendar(year, month)
    for week in month_days:
        day_buttons = []
        for day in week:
            if day != 0:
                day_buttons.append(InlineKeyboardButton(str(day), callback_data=f'date_{day}.{month}.{year}'))
            else:
                day_buttons.append(InlineKeyboardButton(" ", callback_data='ignore'))
        keyboard.add(*day_buttons)

    keyboard.add(InlineKeyboardButton(f"{next_month} {year} >>", callback_data=f'nextmonth_{month}_{year}'))
    return keyboard

