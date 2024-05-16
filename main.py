import telebot
from telebot import types
from database import db
from models import User
from busy_slots import divide_into_hourly_intervals
from config import TOKEN, TECH_SUPPORT_SPECIALIST_ID, ADMIN_PHONE_NUMBER
import ast
from datetime import datetime
from registration import get_current_date, create_register_form



from menu import (
    create_main_menu,
    create_services_menu,
    create_spare_parts_menu,
    create_view_orders_menu,
    create_pagination_buttons
)
from inline_calendar import generate_inline_calendar


bot = telebot.TeleBot(TOKEN)
glob_order = {}
confirm_stage = False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = db.get_user_by_telegram_id(message.chat.id)
    if user:
        bot.reply_to(message, "С возвращением!")
        main_menu = create_main_menu()
        

        service_name = "Наш автосервис"
        work_schedule = "Понедельник-пятница, с 9:00 до 18:00"
        address = "город Москва, улица, дом, ближайшее метро"
        description = "Добро пожаловать в наш автосервис! Мы предоставляем широкий спектр автомобильных услуг."

        welcome_message = (
            f"Добро пожаловать в {service_name}!\n\n"
            f"🕒 График работы: {work_schedule}\n"
            f"📍 Адрес: {address}\n"
            f"📝 Описание: {description}\n"
            f"📞 Контактный телефон: {ADMIN_PHONE_NUMBER}\n\n"
            "Чем мы можем помочь вам сегодня?"
        )
        
        bot.send_message(message.chat.id, welcome_message, reply_markup=main_menu)
        # bot.send_message(message.chat.id, "Вот главное меню:", reply_markup=main_menu)
    else:
        bot.reply_to(message, "Добро пожаловать в бот автосервиса\nПожалуйста, зарегистрируйтесь, чтобы продолжить.")
        registration_form = create_register_form()
        bot.send_message(message.chat.id, "Пожалуйста, зарегистрируйтесь, чтобы продолжить:", reply_markup=registration_form)


@bot.callback_query_handler(func=lambda call: call.data == 'send_contact')
def register_user(call):
    bot.send_message(call.message.chat.id, "Пожалуйста, поделитесь своей контактной информацией.", 
                     reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(types.KeyboardButton('Share Contact', request_contact=True)))

@bot.message_handler(content_types=['contact'])
def save_user(message):
    contact_data = message.contact
    # print(contact_data)
    user_id = contact_data.user_id
    first_name = contact_data.first_name
    last_name = contact_data.last_name
    phone_number = contact_data.phone_number
    dt = get_current_date()
    user_info = [first_name, last_name, phone_number, user_id, dt, 'active']
    bot.send_message(message.chat.id, "Пожалуйста, укажите свой адрес электронной почты")
    
    bot.register_next_step_handler(message, save_user_with_email, user_info)


def save_user_with_email(message, user_info):
    email = message.text
    user_info.append(email)
    db.add_user(tuple(user_info))
    bot.send_message(message.chat.id, "Вы успешно зарегистрированы!")
    main_menu = create_main_menu()
    bot.send_message(message.chat.id, "Вот главное меню:", reply_markup=main_menu)



@bot.callback_query_handler(func=lambda call:call.data.startswith("show_services"))
def show_services_menu(call):
    user = db.get_user_by_telegram_id(call.message.chat.id)
    if not user:
        registration_form = create_register_form()
        bot.send_message(call.message.chat.id, "Пожалуйста, зарегистрируйтесь, чтобы продолжить:", reply_markup=registration_form)
        return
    if call.data.startswith("show_services"):
        in_message = "Вот наши услуги"
    else:
        in_message = "Выберите услугу для заказа"
    dt = call.data
    page = 1
    if len(dt.split("_")) > 2:
        page = int(dt.split("_")[2])
    # print(page)
    cid = call.message.chat.id
    bot.delete_message(cid, call.message.message_id)
    services_menu = create_services_menu(page)
    bot.send_message(call.message.chat.id, in_message, reply_markup=services_menu)


@bot.callback_query_handler(func=lambda call: call.data == 'back_to_main')
def back_to_main_menu(call):
    user = db.get_user_by_telegram_id(call.message.chat.id)
    cid = call.message.chat.id
    bot.delete_message(cid, call.message.message_id)
    if not user:
        registration_form = create_register_form()
        bot.send_message(cid, "Пожалуйста, зарегистрируйтесь, чтобы продолжить:", reply_markup=registration_form)
        return


    main_menu = create_main_menu()
    bot.send_message(call.message.chat.id, "Вот главное меню:",  reply_markup=main_menu)


@bot.message_handler(commands=['menu'])
def main_menu(message):
    user = db.get_user_by_telegram_id(message.chat.id)
    if not user:
        registration_form = create_register_form()
        bot.send_message(message.chat.id, "Пожалуйста, зарегистрируйтесь, чтобы продолжить:", reply_markup=registration_form)
        return
    cid = message.chat.id
    bot.delete_message(cid, message.message_id)
    main_menu = create_main_menu()
    bot.send_message(cid, "Вот главное меню:",  reply_markup=main_menu)


@bot.callback_query_handler(func=lambda call: call.data.startswith("show_spare_parts"))
def show_spare_parts_menu(call):
    user = db.get_user_by_telegram_id(call.message.chat.id)
    if not user:
        registration_form = create_register_form()
        bot.send_message(call.message.chat.id, "Пожалуйста, зарегистрируйтесь, чтобы продолжить:", reply_markup=registration_form)
        return
    dt = call.data
    page = 1
    if len(dt.split("_")) > 3:
        page = int(dt.split("_")[3])
    # print(page)

    spare_parts_menu = create_spare_parts_menu(page)

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=spare_parts_menu)

@bot.callback_query_handler(func=lambda call: call.data.startswith("about_spare_part"))
def show_spare_parts_menu(call):
    user = db.get_user_by_telegram_id(call.message.chat.id)
    if not user:
        registration_form = create_register_form()
        bot.send_message(call.message.chat.id, "Пожалуйста, зарегистрируйтесь, чтобы продолжить:", reply_markup=registration_form)
        return
    part_id = int(call.data.split("_")[-1])
    spare_part = db.get_spare_part_by_id(part_id)
    cid = call.message.chat.id
    bot.delete_message(cid, call.message.message_id)

    part_info_message = f"Запасная часть: {spare_part.title}\n\nОписание: {spare_part.description}\n\nСовместимость: {spare_part.compatibility_info}\n\nЦена: {spare_part.price}\n\nStock Наличие: {spare_part.stock_availability}"


    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    back_button = types.InlineKeyboardButton("Назад", callback_data="show_spare_parts")
    inline_keyboard.add(back_button)
    bot.send_message(call.message.chat.id, part_info_message, reply_markup=inline_keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("show_service"))
def show_service_info(call):
    user = db.get_user_by_telegram_id(call.message.chat.id)
    if not user:
        registration_form = create_register_form()
        bot.send_message(call.message.chat.id, "Пожалуйста, зарегистрируйтесь, чтобы продолжить:", reply_markup=registration_form)
        return
    cid = call.message.chat.id
    service_id = int(call.data.split("_")[-1])

    service = db.get_service_by_id(service_id)

    bot.delete_message(cid, call.message.message_id)
    service_info_message = f"Услуга : {service.name}\n\nОписание: {service.description}\n\nСредняя стоимость: {service.average_cost}\n\nПредполагаемое время завершения: {service.estimated_completion_time}"
    create_order_button = types.InlineKeyboardButton("Создать заказ", callback_data=f"create_order_{service_id}")
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard.add(create_order_button, back_button)

    bot.send_message(call.message.chat.id, service_info_message, reply_markup=inline_keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("create_order"))
def create_order(call):
    user = db.get_user_by_telegram_id(call.message.chat.id)

    if not user:
        registration_form = create_register_form()
        bot.send_message(call.message.chat.id, "Пожалуйста, зарегистрируйтесь, чтобы продолжить:", reply_markup=registration_form)
        return
    dt = call.data
    service_id = ""
    if len(dt.split("_")) > 2:
        service_id = int(call.data.split("_")[-1])
    else:
        show_services_menu(call)
        return
    service = db.get_service_by_id(service_id)

    order_details = {"user_id": call.message.chat.id,
                    "service_id": service_id,
                    "service_type": service.name,
                    "service_cost": service.average_cost
                    }
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(call.message.chat.id, f"Вы выбрали услугу {service.name}. Приступаем к созданию заказа.\nПожалуйста, укажите регистрационный номер автомобиля:")

    bot.register_next_step_handler(call.message, get_vehicle_registration, order_details)

def get_vehicle_registration(message, order_details):
    order_details["vehicle_registration"] = message.text

    bot.send_message(message.chat.id, "Пожалуйста, укажите марку автомобиля:")

    bot.register_next_step_handler(message, get_make, order_details)

def get_make(message, order_details):
    order_details["make"] = message.text

    bot.send_message(message.chat.id, "Укажите год выпуска вашего автомобиля:")

    bot.register_next_step_handler(message, get_year_of_issue, order_details)

def get_year_of_issue(message, order_details):
    order_details["year_of_issue"] = message.text

    bot.send_message(message.chat.id, "Кто будет покупать расходные материалы? Введите: автовладелец или авnосервис")

    bot.register_next_step_handler(message, choose_buyer_of_costomables, order_details)


def choose_buyer_of_costomables(message, order_details):
    order_details["buys_consumables"] = message.text

    bot.send_message(message.chat.id, "Пожалуйста, укажите модель автомобиля:")

    bot.register_next_step_handler(message, get_model, order_details)


def get_model(message, order_details):
    global glob_order
    order_details["model"] = message.text
    glob_order = order_details.copy()
    bot.send_message(message.chat.id, "Пожалуйста, выберите планируемую дату исполнения заказа:", reply_markup=generate_inline_calendar())




def process_planned_date(message, order_details, selected_date):
    order_details['planned_date'] = selected_date
    busy_slots = db.get_or_create_busy_slots(selected_date)
    # print(busy_slots.date, busy_slots.busy_slots)
    intervals = divide_into_hourly_intervals(selected_date)
    busy_hours = ast.literal_eval(busy_slots.busy_slots)
    # print(busy_hours)
    free_hours = []
    for i in intervals:
        if i not in busy_hours:
            free_hours.append(i)

    # print(free_hours)
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "Пожалуйста, укажите планируемое время оказания услуги (например, 09:00, 14:00 и т. д.):")
    bot.send_message(message.chat.id, f"Вот свободные часы: {free_hours}")

    bot.register_next_step_handler(message, process_planned_time, order_details, busy_hours, free_hours)


def process_planned_time(message, order_details, busy_hours, free_hours):
    global confirm_stage
    time_format = "%H:%M"

    try:
        planned_time = datetime.strptime(message.text, time_format).strftime(time_format)
        if planned_time not in free_hours:
            bot.send_message(message.chat.id, "Пожалуйста, выберите час из свободных часов:")
            bot.send_message(message.chat.id, f"Вот свободные часы: {free_hours}")
            bot.register_next_step_handler(message, process_planned_time, order_details, busy_hours, free_hours)
            return 
        order_details["planned_time"] = planned_time
        busy_hours.append(planned_time)
        db.update_busy_slot(order_details["planned_date"], str(busy_hours))
        bot.send_message(message.chat.id, "Пожалуйста, укажите дополнительные сведения или введите 'подтвердить', чтобы подтвердить заказ:")
        confirm_stage = True
        print(order_details)
        bot.register_next_step_handler(message, confirm_order, order_details)
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат времени. Укажите планируемое время в формате ЧЧ:MM (например, 09:00, 14:00 и т. д.):")
        bot.send_message(message.chat.id, f"Вот свободные часы: {free_hours}")
        bot.register_next_step_handler(message, process_planned_time, order_details, busy_hours, free_hours)


def confirm_order(message, order_details):
    global confirm_stage
    if message.text.lower() == "подтвердить":
        inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
        main_menu = types.InlineKeyboardButton("Главное меню", callback_data="back_to_main")
        view_orders = types.InlineKeyboardButton("Просмотр заказов", callback_data="view_orders")
        inline_keyboard.add(main_menu, view_orders)
        order_details["creation_date"] = get_current_date() 
        order_details["additional_details"] = ""
        bot.send_message(message.chat.id, f"Ваш заказ на услугу {order_details['service_type']} был создан со следующими данными:\n\n"
                                          f"Регистрация транспортного средства: {order_details['vehicle_registration']}\n"
                                          f"Марка: {order_details['make']}\n"
                                          f"Модель: {order_details['model']}\n"
                                          f"Год выпуска: {order_details['year_of_issue']}\n"
                                          f"Покупает расходные материалы: {order_details['buys_consumables']}\n"
                                          f"Тип услуги: {order_details['service_type']}\n"
                                          f"Стоимость услуги: {order_details['service_cost']}\n"
                                          f"Планируемая дата: {order_details['planned_date']}\n"
                                          f"Комментарии: {order_details['additional_details']}\n\n"
                                          f"Спасибо за заказ! Для уточнения деталей, можно связаться с администратором автосервиса по номеру: {ADMIN_PHONE_NUMBER}",
                                          reply_markup=inline_keyboard
                                          )
        db.save_order_details(order_details)
        # print(order_details)
    elif message.text.lower() == "отменить":
        confirm_stage = False
        bot.send_message(message.chat.id, "Создание заказа отменено.")
    else:
        order_details["additional_details"] = message.text

        confirmation_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        confirm_button = types.KeyboardButton("Подтвердить")
        cancel_button = types.KeyboardButton("Отменить")
        confirmation_keyboard.row(confirm_button, cancel_button)
        bot.send_message(message.chat.id, "Пожалуйста, подтвердите или отмените заказ:", reply_markup=confirmation_keyboard)
        bot.register_next_step_handler(message, handle_confirm_order, order_details)


def handle_confirm_order(message, order_details):
    global confirm_stage
    if message.text.lower() == "подтвердить":
        inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
        main_menu = types.InlineKeyboardButton("Главное меню", callback_data="back_to_main")
        view_orders = types.InlineKeyboardButton("Просмотр заказов", callback_data="view_orders")
        inline_keyboard.add(main_menu, view_orders)
        bot.send_message(message.chat.id, f"Ваш заказ на услугу {order_details['service_type']} был создан со следующими данными:\n\n"
                                          f"Регистрация транспортного средства: {order_details['vehicle_registration']}\n"
                                          f"Марка: {order_details['make']}\n"
                                          f"Модель: {order_details['model']}\n"
                                          f"Тип услуги: {order_details['service_type']}\n"
                                          f"Стоимость услуги: {order_details['service_cost']}\n"
                                          f"Планируемая дата: {order_details['planned_date']}\n\n"
                                          f"Комментарии: {order_details['additional_details']}\n\n"
                                          f"Спасибо за заказ! Для уточнения деталей, можно связаться с администратором автосервиса по номеру: {ADMIN_PHONE_NUMBER}",
                                          reply_markup=inline_keyboard
                                          )
        order_details["creation_date"] = get_current_date()
        db.save_order_details(order_details)
        # print(order_details)
    elif message.text.lower() == "отменить":
        confirm_stage = False
        bot.send_message(message.chat.id, "Создание заказа отменено.")

@bot.message_handler(func=lambda message: message.text.lower() == "отменить" and not confirm_stage)
def cancel_order_during_vehicle_registration(message):
    global confirm_stage
    confirm_stage = False
    bot.send_message(message.chat.id, "Создание заказа отменено.")



@bot.callback_query_handler(lambda call: call.data.startswith('prevmonth') or call.data.startswith('nextmonth'))
def change_calendar_month(call):
    cid = call.message.chat.id

    inline_message = "Пожалуйста, выберите планируемую дату проведения службы:"
    if call.data == "order_deadline":
        inline_commands = generate_inline_calendar()
    elif call.data.startswith("nextmonth"):
        # print(call.data.split("_"))
        # print(call.data)
        month = int(call.data.split("_")[1]) + 1
        year = int(call.data.split("_")[2])
        if month == 13:
            month = 1
            year += 1

        inline_commands = generate_inline_calendar(year, month)
    elif call.data.startswith("prevmonth"):
        # print(call.data.split("_"))
        # print(call.data)
        month = int(call.data.split("_")[1]) - 1
        year = int(call.data.split("_")[2]) 

        if month == 0:
            month = 12
            year -= 1
        inline_commands = generate_inline_calendar(year, month)
    bot.delete_message(cid, call.message.message_id)
    bot.send_message(cid, inline_message, reply_markup=inline_commands, parse_mode='Markdown')


@bot.callback_query_handler(lambda call: call.data.startswith('date'))
def change_calendar_month(call):
    global glob_order
    sel_date = call.data.split("_")[-1]
    # print(sel_date)
    process_planned_date(call.message, glob_order, sel_date)



@bot.message_handler(commands=['modify_order'])
def modify_order(message):
    pass

@bot.message_handler(commands=['cancel_order'])
def cancel_order(message):
    pass

@bot.message_handler(commands=['chat_admin'])
def chat_admin(message):
    pass


@bot.callback_query_handler(func=lambda call: call.data.startswith("view_orders"))
def view_orders(call):
    user = db.get_user_by_telegram_id(call.message.chat.id)
    if not user:
        registration_form = create_register_form()
        bot.send_message(call.message.chat.id, "Пожалуйста, зарегистрируйтесь, чтобы продолжить:", reply_markup=registration_form)
        return
    user_id = call.message.chat.id
    dt = call.data
    cid = call.message.chat.id
    page = 1
    if len(dt.split("_")) > 2:
        page = int(dt.split("_")[2])
    # print(page)

    orders_menu = create_view_orders_menu(user_id, page)
    bot.delete_message(cid, call.message.message_id)
    bot.send_message(cid, "Ваши заказы:", reply_markup=orders_menu)





@bot.callback_query_handler(func=lambda call: call.data.startswith("show_order"))
def show_order_info(call):
    user = db.get_user_by_telegram_id(call.message.chat.id)
    if not user:
        registration_form = create_register_form()
        bot.send_message(call.message.chat.id, "Пожалуйста, зарегистрируйтесь, чтобы продолжить:", reply_markup=registration_form)
        return
    cid = call.message.chat.id
    order_id = int(call.data.split("_")[-1])

    order = db.get_order_by_id(order_id)

    order_info_message = f"ID заказа: {order.id}\n\n" \
                         f"Регистрация автомобиля: {order.vehicle_registration}\n" \
                         f"Марка: {order.make}\n" \
                         f"Модель: {order.model}\n" \
                         f"Тип услуги: {order.service_type}\n" \
                         f"Стоимость услуги: {order.service_cost}\n" \
                         f"Год выпуска: {order.year_of_issue}\n" \
                         f"Покупает расходные материалы: {order.buys_consumables}\n" \
                         f"Планируемая дата: {order.planned_date}\n" \
                         f"Дата создания: {order.creation_date}\n" \
                         f"Статус: {order.status}\n" \
                         f"Комментарии: {order.comments}"
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    delete_button = types.InlineKeyboardButton(f"Отменить", callback_data=f"cancle_order_{order.id}")
    edit_button = types.InlineKeyboardButton(f"Добавить комментарий", callback_data=f"add_comment_{order.id}")

    inline_keyboard.add(edit_button, delete_button)
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard.add(back_button)
    bot.delete_message(cid, call.message.message_id)
    bot.send_message(call.message.chat.id, order_info_message, reply_markup=inline_keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('add_comment'))
def add_comment(call):
    order_id = int(call.data.split('_')[-1])
    bot.delete_message(call.message.chat.id, call.message.message_id)
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    back_button = types.InlineKeyboardButton("Отмена", callback_data="back_to_main")
    inline_keyboard.add(back_button)
    bot.send_message(call.message.chat.id, "Пожалуйста, оставьте комментарий к этому заказу:", reply_markup=inline_keyboard)
    bot.register_next_step_handler(call.message, lambda message: process_comment(message, order_id))


def process_comment(message, order_id):
    comment = message.text
    db.order_add_comment(order_id, comment)
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard.add(back_button)
    bot.send_message(message.chat.id, "Ваш комментарий успешно добавлен к заказу!", reply_markup=inline_keyboard)
    admin_inline = types.InlineKeyboardMarkup(row_width=2)
    
    see_order = types.InlineKeyboardButton("Посмотреть заказ", callback_data=f"admin_show_order_{order_id}")
    admin_inline.add(see_order)
    bot.send_message(ADMIN_IDS[0], f"Пользователь добавляет комментарий к заказу с ID {order_id}", reply_markup=admin_inline)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cancle_order"))
def user_cancle_delete_order(call):
    message = call.message
    order_id = int(call.data.split("_")[-1])

    bot.delete_message(message.chat.id, message.id)
    db.delete_order_by_id(order_id)

    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard.add(back_button)
    bot.send_message(message.chat.id, f"заказ с ID {order_id} был успешно удален", reply_markup=inline_keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("show_feedbacks"))
def show_feedbacks(call):
    page = int(call.data.split("_")[-1])
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)

    feedbacks = db.get_feedbacks_by_page(page)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if not feedbacks:
        back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
        inline_keyboard.add(back_button)
        leave_feedback_button = types.InlineKeyboardButton("Оставить отзыв", callback_data="leave_feedback")
        inline_keyboard.row(leave_feedback_button)
        bot.send_message(call.message.chat.id, "Пока нет отзывов", reply_markup=inline_keyboard)
        return

    feedback_message = "Вот отзывы:\n\n"
    for feedback in feedbacks:
        user = db.get_user_by_telegram_id(feedback.user_id)
        feedback_message += f"Пользователь: {user.first_name}\n"
        feedback_message += f"Обратная связь: {feedback.text}\n"
        feedback_message += f"Оценка: {feedback.rating}\n"
        feedback_message += f"Было отправлено: {feedback.timestamp}\n\n"
        feedback_message += f"----------------------------------\n\n"

    pagination_buttons = create_pagination_buttons(page, "show_feedbacks")
    inline_keyboard.row(*pagination_buttons)
    leave_feedback_button = types.InlineKeyboardButton("Оставить отзыв", callback_data="leave_feedback")
    inline_keyboard.row(leave_feedback_button)
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard.add(back_button)
    bot.send_message(call.message.chat.id, feedback_message, reply_markup=inline_keyboard)





@bot.callback_query_handler(func=lambda call: call.data == 'leave_feedback')
def feedback_button_handler(call):
    user_id = call.message.chat.id
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(user_id, "Пожалуйста, оставьте свой отзыв и оценку (1–5), разделенные запятой \nнапример: «Отличное обслуживание, 5».")
    
    bot.register_next_step_handler(call.message, process_feedback)

def process_feedback(message):
    if len(message.text.split(',')) != 2:
        user_id = message.chat.id
        bot.send_message(user_id, "Пожалуйста, оставьте свой отзыв и оценку через запятую. Например: «Отличное обслуживание, 5».")
        bot.register_next_step_handler(message, process_feedback)
        return
    feedback_text, rating = message.text.split(',')

    rating = int(rating)
    
    if 1 <= rating <=5:
        inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
        back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
        inline_keyboard.add(back_button)
        db.insert_feedback(message.chat.id, feedback_text, rating)
        bot.send_message(message.chat.id, "Спасибо за ваш отзыв! Ждём Вас снова!", reply_markup=inline_keyboard)
    else:
        bot.reply_to(message, "Неверный рейтинг. Укажите число от 1 до 5.")
        bot.register_next_step_handler(message, process_feedback)
        return
    


@bot.callback_query_handler(func=lambda call: call.data.startswith("faq"))
def faq_button_handler(call):
    page = int(call.data.split('_')[-1])
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)

    bot.delete_message(call.message.chat.id, call.message.id)

    faqs = db.get_faqs_by_page(page)
    if not faqs:
        back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
        inline_keyboard.add(back_button)
        bot.send_message(call.message.chat.id, "Нет доступных часто задаваемых вопросов.", reply_markup=inline_keyboard)
        return

    message = "Часто задаваемые вопросы:\n\n"
    for num,faq in enumerate(faqs):
        message += f"*{num+1}. {faq.question}*\n{faq.answer}\n\n"

    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    pagination_buttons = create_pagination_buttons(page, "faq")
    inline_keyboard.row(*pagination_buttons)
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard.add(back_button)
    bot.send_message(call.message.chat.id, message, reply_markup=inline_keyboard,  parse_mode= 'Markdown')

@bot.callback_query_handler(func=lambda call: call.data == 'tech_support')
def create_tech_support_menu(call):
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    bot.delete_message(call.message.chat.id, call.message.id)
    support_text = "Если вам нужна техническая поддержка или у вас есть вопросы, отправьте нам сообщение.\n"
    support_text += f"Или позвоните администратору по этому номеру {ADMIN_PHONE_NUMBER}" 
    support_button = types.InlineKeyboardButton("Отправить сообщение в поддержку", callback_data="contact_support")
    see_button = types.InlineKeyboardButton("Ваши сообщения", callback_data="see_messages_1")
    inline_keyboard.add(see_button)
    inline_keyboard.add(support_button)

    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, support_text, reply_markup=inline_keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'contact_support')
def create_tech_support_menu(call):
    user = db.get_user_by_telegram_id(call.message.chat.id)
    bot.delete_message(call.message.chat.id, call.message.id)
    support_text = "Вы можете отправить ваше сообщение здесь, и мы ответим вам как можно скорее.\n"

    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, support_text, reply_markup=inline_keyboard)
    bot.register_next_step_handler(call.message, save_request_to_support,user)

def save_request_to_support(message, user):

    support_message_id = db.insert_message_to_support(message.text, user.telegram_id)
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)

    see_button = types.InlineKeyboardButton("Ваши сообщения", callback_data="see_messages_1")

    inline_keyboard.add(back_button, see_button)
    bot.reply_to(message, ".")
    bot.send_message(message.chat.id, "Ваше сообщение получено. Мы ответим вам как можно скорее.", reply_markup=inline_keyboard)
    
    support_keyboard =  types.InlineKeyboardMarkup(row_width=2)
    see_message_button = types.InlineKeyboardButton("Просмотреть сообщение", callback_data=f"see_user_message_{support_message_id}")
    support_keyboard.add(see_message_button)
    if TECH_SUPPORT_SPECIALIST_ID:
        bot.send_message(TECH_SUPPORT_SPECIALIST_ID, f"Пользователь {user.first_name}({user.telegram_id})отправил сообщение в поддержку", reply_markup=support_keyboard)
    else:
        bot.send_message(ADMIN_IDS[0], f"Пользователь {user.first_name} ({user.telegram_id})  отправил сообщение в поддержку", reply_markup=support_keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('see_user_message'))
def see_user_message(call):
    support_message_id = int(call.data.split('_')[-1])
    bot.delete_message(call.message.chat.id, call.message.id)
    message = db.get_message_by_id(support_message_id)
    user = db.get_user_by_telegram_id(message.user_id)
    info = f"ID сообщения: {message.id}\n"
    info += f"Сообщение от пользователя {user.first_name} ({user.telegram_id}):\n\n"
    info += f"Сообщение: {message.message}\n"
    info += f"Отправлено: {message.sent}\n\n"
    support_keyboard =  types.InlineKeyboardMarkup(row_width=2)
    reply_to_message = types.InlineKeyboardButton("Ответить на сообщение", callback_data=f"reply_to_message_{support_message_id}")
    support_keyboard.add(reply_to_message)
    bot.send_message(TECH_SUPPORT_SPECIALIST_ID, info, reply_markup=support_keyboard)

    db.change_message_status(support_message_id, "Просмотрено")

    bot.send_message(message.user_id, f"Ваше сообщение с ID {support_message_id} было просмотрено.")


@bot.message_handler(commands=['unanswered_messages'])
def create_tech_support_menu(message):
    if message.chat.id != TECH_SUPPORT_SPECIALIST_ID:
        bot.send_message(message.chat.id, "У вас нет разрешения на использование этой команды")
        return
    messages = db.get_messages_by_status("Отвечено", invert=True)

    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    if messages:
        for sp_message in messages:
            sp_message_button = types.InlineKeyboardButton(f"ID сообщения: {sp_message.id}\nПользователь: {sp_message.user_id}", callback_data=f"see_user_message_{sp_message.id}")
            inline_keyboard.add(sp_message_button)

    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard.add(back_button)

    bot.send_message(message.chat.id, "Вот все сообщения без ответа:", reply_markup=inline_keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_profile'))
def edit_profile(call):
    user = db.get_user_by_telegram_id(call.message.chat.id)
    bot.delete_message(call.message.chat.id, call.message.id)

    user_info = f"Информация о пользователе:\n\n"
    user_info += f"Имя: {user.first_name}\n"
    user_info += f"Фамилия: {user.last_name}\n"
    user_info += f"Номер телефона: {user.phone_number}\n"
    user_info += f"E-mail: {user.email}\n"
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)

    edit_first_name_button = types.InlineKeyboardButton(f"Имя: {user.first_name}", callback_data="edit_first_name")
    edit_last_name_button = types.InlineKeyboardButton(f"Фамилия: {user.last_name}", callback_data="edit_last_name")
    edit_phone_number_button = types.InlineKeyboardButton(f"Номер телефона: {user.phone_number}", callback_data="edit_phone_number")
    edit_email_button = types.InlineKeyboardButton(f"E-mail: {user.email}", callback_data="edit_email")

    inline_keyboard.add(edit_first_name_button)
    inline_keyboard.add(edit_last_name_button)
    inline_keyboard.add(edit_phone_number_button)
    inline_keyboard.add(edit_email_button)

    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard.add(back_button)
    bot.send_message(call.message.chat.id, f"Информация о пользователе:", reply_markup=inline_keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'edit_phone_number')
def edit_phone_number(call):
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)    
    back_button = types.InlineKeyboardButton("Отмена", callback_data="back_to_main")
    inline_keyboard.add(back_button)
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(call.message.chat.id, "Пожалуйста, введите новый номер телефона:", reply_markup=inline_keyboard)
    bot.register_next_step_handler(call.message, process_new_phone_number)

def process_new_phone_number(message):
    new_phone_number = message.text
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)    
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard.add(back_button)
    db.update_user_field(message.chat.id, 'phone_number', new_phone_number)
    bot.send_message(message.chat.id, "Ваш номер телефона успешно обновлен!", reply_markup=inline_keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'edit_email')
def edit_email(call):
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)    
    back_button = types.InlineKeyboardButton("Отмена", callback_data="back_to_main")
    inline_keyboard.add(back_button)
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(call.message.chat.id, "Пожалуйста, введите новый адрес электронной почты:", reply_markup=inline_keyboard)
    bot.register_next_step_handler(call.message, process_new_email)

def process_new_email(message):
    new_email = message.text
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)    
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard.add(back_button)
    db.update_user_field(message.chat.id, 'email', new_email)
    bot.send_message(message.chat.id, "Ваш адрес электронной почты успешно обновлен!", reply_markup=inline_keyboard)



@bot.callback_query_handler(func=lambda call: call.data == 'edit_first_name')
def edit_first_name(call):
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)    
    back_button = types.InlineKeyboardButton("Отмена", callback_data="back_to_main")
    inline_keyboard.add(back_button)
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(call.message.chat.id, "Введите свое новое имя:", reply_markup=inline_keyboard)
    bot.register_next_step_handler(call.message, process_new_first_name)



def process_new_first_name(message):
    new_first_name = message.text
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)    
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard.add(back_button)
    db.update_user_field(message.chat.id, 'first_name', new_first_name)
    bot.send_message(message.chat.id, "Ваше имя успешно обновлено!", reply_markup=inline_keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'edit_last_name')
def edit_last_name(call):
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)    
    back_button = types.InlineKeyboardButton("Отмена", callback_data="back_to_main")
    inline_keyboard.add(back_button)
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(call.message.chat.id, "Введите новую фамилию:", reply_markup=inline_keyboard)
    bot.register_next_step_handler(call.message, process_new_last_name)


def process_new_last_name(message):
    new_last_name = message.text
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)    
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard.add(back_button)
    db.update_user_field(message.chat.id, 'last_name', new_last_name)
    bot.send_message(message.chat.id, "Ваша фамилия успешно обновлена!", reply_markup=inline_keyboard)





@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_to_message'))
def see_user_message(call):
    support_message_id = int(call.data.split('_')[-1])
    message = db.get_message_by_id(support_message_id)
    user = db.get_user_by_telegram_id(message.user_id)
    info = f"ID сообщения: {message.id}\n"
    info += f"Сообщение от пользователя {user.first_name} ({user.telegram_id}):\n\n"
    info += f"Сообщение: {message.message}\n"
    info += f"Отправлено: {message.sent}\n\n"
    bot.delete_message(call.message.chat.id, call.message.id)
    message = db.get_message_by_id(support_message_id)
    bot.send_message(TECH_SUPPORT_SPECIALIST_ID, info)
    bot.register_next_step_handler(call.message, reply_from_support, user, message)


def reply_from_support(message, user, support_message):
    db.change_message_status(support_message.id, "Отвечено")
    bot.send_message(support_message.user_id, f"На ваше сообщение с ID {support_message.id} ответили")
    info = f"Сообщение: {support_message.message}\n"
    info += f"Отправлено: {support_message.sent}\n\n"
    bot.send_message(support_message.user_id, info)
    support_keyboard =  types.InlineKeyboardMarkup(row_width=2)
    main_menu = types.InlineKeyboardButton("Ваши сообщения", callback_data=f"see_messages_1")
    support_keyboard.add(main_menu)

    bot.send_message(support_message.user_id,f"Ответ: {message.text}" , reply_markup=support_keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('see_messages'))
def see_messages(call):
    page = int(call.data.split("_")[-1])
    messages = db.get_messages_by_user_id_and_page(call.message.chat.id, page)
    bot.delete_message(call.message.chat.id, call.message.id)
    # Create a message to display the messages
    response = "Вот ваши сообщения, отправленные в службу поддержки:\n\n"
    for message in messages:
        response += f"ID сообщения: {message.id}\n"
        response += f"Сообщение: {message.message}\n"
        response += f"Статус: {message.status}\n\n"
        response += f"Отправлено: {message.sent}\n\n"

    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)

    pagination_buttons = create_pagination_buttons(page, f"see_messages_{call.message.chat.id}")
    inline_keyboard.row(*pagination_buttons)


    inline_keyboard.add(back_button)
    bot.send_message(call.message.chat.id, response, reply_markup=inline_keyboard)

from admin import *
from scheduling import *

if __name__ == '__main__':
    db.create_tables() 
    # db.populate_faq()
    db.populate_services_table()
    # db.populate_spare_parts_table()
    # db.populate_users_table()
    # db.populate_feedbacks()

    reminder_thread = threading.Thread(target=reminder_sender)
    reminder_thread.start()
    print("reminder was started")
    bot.polling()
 

