import time
from datetime import datetime, timedelta
from telebot import types
import threading
from main import bot 
from database import db
import pytz
from config import TIME_ZONE


tz = pytz.timezone(TIME_ZONE)

def reminder_sender():


    back_button = types.InlineKeyboardButton("Меню", callback_data="show_spare_parts")

    while True:
        orders = db.get_all_orders()  
        for order in orders:
            inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
            reject_button = types.InlineKeyboardButton(f"Отменить", callback_data=f"schedule_cancle_order_{order.id}")
            confirmed_button1 = types.InlineKeyboardButton("Подтвердить", callback_data=f"schedule_confirm_order_{order.id}")
            confirmed_button2 = types.InlineKeyboardButton("Подтвердить", callback_data=f"schedule_order_confirmation_{order.id}")
            order_button = types.InlineKeyboardButton(f"Посмотреть заказ", callback_data=f"show_order_{order.id}")
            
            date_format = '%d.%m.%Y'
            hour_format = "%H:%M"
            planned_time = datetime.strptime(order.planned_time, hour_format) 
            # print(planned_time)
            planned_date = datetime.strptime(order.planned_date, date_format)
            reminder_date = planned_date - timedelta(days=1)
            current_date = datetime.now(tz)
            current_time = datetime.now(tz).time()
            time_difference = datetime.combine(datetime.today().date(), planned_time.time()) - datetime.combine(datetime.today(), current_time)

            if time_difference <= timedelta(hours=1) and time_difference >= timedelta(hours=0) and current_date.date() == planned_date.date() and  order.status not in ["Отменено", "Меньше часа"]:
                inline_keyboard.add(reject_button ,confirmed_button2)
                inline_keyboard.add(back_button, order_button)
                reminder_message = f"Вы записаны на услугу {order.service_type} в {order.planned_time} часов. Пожалуйста, подтвердите Ваш приезд"
                bot.send_message(chat_id=order.user_id, text=reminder_message, reply_markup=inline_keyboard)
            elif current_date.date() == reminder_date.date() and order.status not in ["Отменено", "Подтверждено"]:
                reminder_message = f"Вы записаны {planned_date.strftime('%Y.%m.%d')} в {order.planned_time} на услугу: {order.service_type}.  Пожалуйста, подтвердите Ваш приезд"
                inline_keyboard.add(reject_button ,confirmed_button1)
                inline_keyboard.add(back_button, order_button)
                bot.send_message(chat_id=order.user_id, text=reminder_message, reply_markup=inline_keyboard)
        time.sleep(60) 

@bot.callback_query_handler(func=lambda call: call.data.startswith("schedule_cancle_order"))
def schedule_cancle_order(call):
    order_id = int(call.data.split("_")[-1])
    db.update_order_status(order_id, "Отменено")
    status_message = "Вы отменили заказ"
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    back_button = types.InlineKeyboardButton("Меню", callback_data="back_to_main")
    show_order = types.InlineKeyboardButton("Посмотреть заказ", callback_data=f"show_order_{order_id}")
    inline_keyboard.add(back_button, show_order)
    bot.send_message(call.message.chat.id, text=status_message, reply_markup=inline_keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("schedule_confirm_order"))
def schedule_confirm_order(call):
    order_id = int(call.data.split("_")[-1])
    db.update_order_status(order_id, "Подтверждено")
    status_message = "Спасибо, что подтвердили!"
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    back_button = types.InlineKeyboardButton("Меню", callback_data="back_to_main")
    show_order = types.InlineKeyboardButton("Посмотреть заказ", callback_data=f"show_order_{order_id}")
    inline_keyboard.add(back_button, show_order)
    bot.send_message(call.message.chat.id, text=status_message, reply_markup=inline_keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("schedule_order_confirmation"))
def schedule_confirmation(call):
    order_id = int(call.data.split("_")[-1])
    db.update_order_status(order_id, "Меньше часа")
    status_message = "Спасибо, что подтвердили!"
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    back_button = types.InlineKeyboardButton("Меню", callback_data="back_to_main")
    show_order = types.InlineKeyboardButton("Посмотреть заказ", callback_data=f"show_order_{order_id}")
    inline_keyboard.add(back_button, show_order)
    bot.send_message(call.message.chat.id, text=status_message, reply_markup=inline_keyboard)
