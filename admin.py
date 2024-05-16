from config import ADMIN_IDS, TECH_SUPPORT_SPECIALIST_ID, ADMIN_PHONE_NUMBER
from main import bot
from database import db
from telebot import types
from menu import create_pagination_buttons


# Handler for admin commands
@bot.message_handler(commands=['admin'])
def admin_commands(message):
    # Check if the user is an admin
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "Вы не авторизованы для использования этой команды.")
        return

    # Send admin interface menu
    admin_menu = create_admin_menu()
    bot.send_message(message.chat.id, "Меню администратора", reply_markup=admin_menu)


@bot.callback_query_handler(func=lambda call: call.data.startswith('back_to_admin_menu'))
def back_to_admin_menu(call):
    # Check if the user is an admin
    message = call.message
    
    bot.delete_message(message.chat.id, message.id)
    if call.from_user.id not in ADMIN_IDS:
        print("You are not autherized!!!")
        bot.send_message(message, "Вы не авторизованы для использования этой команды.")
        return

    # Send admin interface menu
    admin_menu = create_admin_menu()
    bot.send_message(message.chat.id, "Меню администратора", reply_markup=admin_menu)

# Handler for processing admin commands
@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def process_admin_command(call):
    cid = call.message.chat.id
    mess = call.message
    if call.from_user.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "You are not authorized to perform this action.")
        return
    command = '_'.join(call.data.split('_')[1:])
    print(command)
    if command.startswith('view_orders'):
        page = int(command.split("_")[-1])
        try:
            user_id = int(command.split("_")[-2])
        except:
            user_id = "all"
        admin_show_orders_by_user(mess, user_id, page)
    elif command.startswith("view_services"):
        page = int(command.split("_")[-1])
        view_services(mess, page)
    elif command.startswith("show_service"):
        service_id = command.split("_")[-1]
        admin_show_service(mess ,service_id)
    elif command.startswith("delete_service"):
        service_id = int(command.split("_")[-1])
        admin_delete_service(mess, service_id)
    elif command.startswith("edit_service"):
        service_id = command.split("_")[-1]
        edit_service(mess ,service_id)
    elif command.startswith('delete_order'):
        order_id = command.split("_")[-1]
        admin_delete_order(mess, order_id)
    elif command.startswith('change_orders_status'):
        order_id = command.split("_")[-1]
        admin_change_orders_status(mess, order_id)
    elif command.startswith('set_order_status'):
        new_status = command.split("_")[-1]
        order_id = int(command.split("_")[-2])
        set_order_status(mess, new_status, order_id)
    elif command.startswith("about_spare_part"):
        part_id = command.split("_")[-1]
        admin_about_spare_part(mess, part_id)
    elif command.startswith('show_order'):
        order_id = command.split("_")[-1]
        admin_show_order(mess, order_id)
    elif command.startswith('view_users'):
        page = int(command.split("_")[-1])
        admin_view_users(mess, page)    
    elif command.startswith("delete_user"):
        user_id = int(command.split("_")[-2])
        admin_delete_user(mess, user_id)
    elif command.startswith('user_info'):
        user_id = int(command.split("_")[-1])
        admin_user_info(mess, user_id)
    elif command == 'add_service':
        add_service(call.message, call.from_user.id)
    elif command == "add_faq":
        add_faq_button_handler(mess)
    elif command == 'add_spare_part':
        admin_add_spare_part(mess)
    elif command.startswith('edit_spare_part'):
        spare_id = int(command.split("_")[-1])
        admin_edit_spare_part(mess, spare_id)
    elif command.startswith("view_spare_parts"):
        page = int(command.split("_")[-1])
        admin_view_spare_parts_menu(mess, page)
    elif command.startswith("delete_spare_part"):
        spare_id = int(command.split("_")[-1])
        admin_delete_spare_part(mess, spare_id)
    elif command.startswith("faq"):
        faq_id = int(command.split("_")[-1])
        admin_faq_button(mess, faq_id)
    elif command.startswith("view_faq"):
        faq_id = int(command.split("_")[-1])
        admin_view_faq(mess, faq_id)
    elif command.startswith("edit_faq"):
        faq_id = int(command.split("_")[-1])
        admin_edit_faq(mess, faq_id)
    elif command.startswith("delete_faq"):
        faq_id = int(command.split("_")[-1])
        admin_delete_faq(mess, faq_id)
    elif command.startswith("support_messages"):
        admin_check_messages(mess)
    elif command.startswith("show_feedbacks"):
        page = int(command.split("_")[-1])
        admin_show_feedbacks(mess, page)
    elif command.startswith("view_archived_orders"):
        page = int(command.split("_")[-1])
        admin_view_archived_orders(mess, page)
    else:
        bot.answer_callback_query(call.id, "Invalid command")


def admin_view_archived_orders(message, page):
    orders_message = "Вот все услуги, которые были заархивированы:\n\n"
    orders = db.get_orders_by_page(page)
    bot.delete_message(message.chat.id, message.id)
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    for order in orders:
        if order.status != "В архиве":
            continue
        order_button = types.InlineKeyboardButton(f"Услуга: {order.service_type}\n\nСтатус: {order.status}\n" ,
                                                  callback_data=f"admin_show_order_{order.id}")
        inline_keyboard.add(order_button)

    pagination_buttons = create_pagination_buttons(page, f"admin_view_archived_orders")
    inline_keyboard.row(*pagination_buttons)    
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    inline_keyboard.add(back_button)

    bot.send_message(message.chat.id, orders_message, reply_markup=inline_keyboard)


def admin_change_orders_status(message, order_id):
    bot.delete_message(message.chat.id, message.id)
    db.get_order_by_id(order_id)
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)

    pending_button = types.InlineKeyboardButton("В ожидании", callback_data=f"admin_set_order_status_{order_id}_В ожидании")
    in_progress_button = types.InlineKeyboardButton("В процессе", callback_data=f"admin_set_order_status_{order_id}_В процессе")
    cancelled_button = types.InlineKeyboardButton("Отменено", callback_data=f"admin_set_order_status_{order_id}_Отменено")
    on_hold_button = types.InlineKeyboardButton("На удержании", callback_data=f"admin_set_order_status_{order_id}_На удержании")
    delayed_button = types.InlineKeyboardButton("Задержано", callback_data=f"admin_set_order_status_{order_id}_Задержано")
    failed_button = types.InlineKeyboardButton("Не выполнено", callback_data=f"admin_set_order_status_{order_id}_Не выполнено")
    ready_button = types.InlineKeyboardButton("Готово", callback_data=f"admin_set_order_status_{order_id}_Готово")
    archive_button = types.InlineKeyboardButton("Архивировать", callback_data=f"admin_set_order_status_{order_id}_В архиве")
    confirmed_button = types.InlineKeyboardButton("Подтверждено", callback_data=f"admin_set_order_status_{order_id}_Подтверждено")


    inline_keyboard.add(pending_button, in_progress_button, ready_button, cancelled_button)
    inline_keyboard.add(delayed_button, archive_button, on_hold_button,confirmed_button )
    inline_keyboard.add(failed_button)

    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    inline_keyboard.add(back_button)
    bot.send_message(message.chat.id, "Выберите новый статус для заказа:", reply_markup=inline_keyboard)

def admin_user_info(message, user_id):
    user = db.get_user_by_id(user_id)
    bot.delete_message(message.chat.id, message.id)

    user_info = f"Информация о пользователе:\n\n"
    user_info += f"ID: {user.id}\n"
    user_info += f"Имя: {user.first_name}\n"
    user_info += f"Фамилия: {user.last_name}\n"
    user_info += f"Номер телефона: {user.phone_number}\n"
    user_info += f"Telegram ID: {user.telegram_id}\n"
    user_info += f"E-mail: {user.email}\n"
    user_info += f"Дата регистрации: {user.registration_date}\n"
    user_info += f"Статус активности: {user.activity_status}\n"
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    back_button = types.InlineKeyboardButton("Назад", callback_data="admin_view_users_1")
    inline_keyboard.add(back_button)
    bot.send_message(message.chat.id, user_info, reply_markup=inline_keyboard)


def set_order_status(message, new_status, order_id):
    db.update_order_status(order_id, new_status)
    bot.delete_message(message.chat.id, message.id)
    status_message = ""
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    back_button = types.InlineKeyboardButton("Меню", callback_data="back_to_main")
    show_order = types.InlineKeyboardButton("Посмотреть заказ", callback_data=f"show_order_{order_id}")
    order = db.get_order_by_id(order_id)

    admin_menu = types.InlineKeyboardMarkup(row_width=2)
    admin_back = types.InlineKeyboardButton("Меню", callback_data="back_to_main")
    admin_menu.add(admin_back)
    if new_status == "В архиве":
        status_message = "Ваш заказ был заархивирован"
    elif new_status == "В ожидании":
        status_message = "Ваш заказ в ожидании. Ожидайте дальнейшей информации о статусе заказа"
    elif new_status == "Не выполнено":
        status_message = f"К сожалению, Ваш заказ не смог быть выполнен. Для уточнения деталей свяжитесь с администратором по номеру {ADMIN_PHONE_NUMBER}"
    elif new_status == "В процессе":
        status_message = "Ваш заказ в процессе. Ожидайте дальнейшей информации о статусе заказа"
    elif new_status == "Готово":
        status_message = "Ваш заказ готов!\n"
        status_message += "Хотели бы Вы оставить отзыв о наших услугах?\n"
        leave_feedback_button = types.InlineKeyboardButton("Оставить отзыв", callback_data="leave_feedback")
        inline_keyboard.row(leave_feedback_button)
        # back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
        bot.send_message(order.user_id, status_message, reply_markup=inline_keyboard)
        return

    elif new_status == "На удержании":
        status_message = "Ваш заказ на удержании. Ожидайте дальнейшей информации о статусе заказа"
        
        bot.send_message(message.chat.id, "Укажите причину: ", reply_markup=admin_menu)
        bot.register_next_step_handler(message, indicate_reason, status_message, order)
        return
    elif new_status == "Отменено":
        status_message = "Ваш заказ был отменён"
        
        bot.send_message(message.chat.id, "Укажите причину: ", reply_markup=admin_menu)
        bot.register_next_step_handler(message, indicate_reason, status_message, order)
        return
    elif new_status == "Задержано":
        status_message = "Ваш заказ был задержан"

        bot.send_message(message.chat.id, "Укажите причину: ", reply_markup=admin_menu)
        bot.register_next_step_handler(message, indicate_reason, status_message, order)
        return 
    else:
        status_message = f"Статус вашего заказа был изменен на {new_status}"
    inline_keyboard.add(show_order, back_button)
    bot.send_message(order.user_id, status_message, reply_markup=inline_keyboard)
    admin_show_order(message, order_id)
    # bot.send_message(message.chat.id, status_message, reply_markup=admin_menu)


def indicate_reason(message, status_message, order):
    status_message += f"\nПо причине: {message.text}\n\n"
    status_message += f"Можете связаться с администратором для уточнения деталей по номеру {ADMIN_PHONE_NUMBER}"

    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    back_button = types.InlineKeyboardButton("Меню", callback_data="back_to_main")
    show_order = types.InlineKeyboardButton("Посмотреть заказ", callback_data=f"show_order_{order.id}")
    inline_keyboard.add(back_button, show_order)
    bot.send_message(order.user_id, status_message, reply_markup=inline_keyboard)
    admin_show_order(message, order.id)
    # bot.send_message(message.chat.id, status_message, reply_markup=admin_menu)


def admin_delete_order(message, order_id):
    bot.delete_message(message.chat.id, message.id)
    db.delete_order_by_id(order_id)

    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    inline_keyboard.add(back_button)
    bot.send_message(message.chat.id, f"заказ с ID {order_id} был успешно удален", reply_markup=inline_keyboard)

def admin_about_spare_part(message, part_id):

    spare_part = db.get_spare_part_by_id(part_id)
    cid = message.chat.id
    bot.delete_message(cid, message.id)

    part_info_message = f"Запасная часть: {spare_part.title}\n\nОписание: {spare_part.description}\n\nСовместимость: {spare_part.compatibility_info}\n\nЦена: {spare_part.price}\n\nStock Наличие: {spare_part.stock_availability}"


    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    back_button = types.InlineKeyboardButton("Назад", callback_data="admin_view_spare_parts_1")
    inline_keyboard.add(back_button)
    bot.send_message(message.chat.id, part_info_message, reply_markup=inline_keyboard)

def admin_show_order(message, order_id):
    bot.delete_message(message.chat.id, message.id)
    order = db.get_order_by_id(order_id)
    print(order.user_id, "teleg user id")
    user = db.get_user_by_telegram_id(int(order.user_id))

    order_info_message = f"Пользователь:  {user.first_name}\n\n" \
                         f"ID пользователя:  {user.telegram_id}\n\n" \
                         f"ID заказа: {order.id}\n\n" \
                         f"Регистрация автомобиля: {order.vehicle_registration}\n" \
                         f"Марка: {order.make}\n" \
                         f"Модель: {order.model}\n" \
                         f"Год выпуска: {order.year_of_issue}\n" \
                         f"Покупает расходные материалы: {order.buys_consumables}\n" \
                         f"Тип услуги: {order.service_type}\n" \
                         f"Стоимость услуги: {order.service_cost}\n" \
                         f"Планируемая дата: {order.planned_date}\n" \
                         f"Дата создания: {order.creation_date}\n" \
                         f"Статус: {order.status}\n" \
                         f"Комментарии: {order.comments}"

    back_to_orders = types.InlineKeyboardMarkup(row_width=2)
    reply_button = types.InlineKeyboardButton("Изменить статус", callback_data=f"admin_change_orders_status_{order.id}")
    delete_button = types.InlineKeyboardButton("Удалить", callback_data=f"admin_delete_order_{order.id}")
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    back_to_orders.add(reply_button, delete_button,back_button)

    bot.send_message(message.chat.id, order_info_message, reply_markup=back_to_orders)



def admin_delete_spare_part(message, spare_part_id):
    bot.delete_message(message.chat.id, message.id)
    db.delete_spare_part_by_id(spare_part_id)
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    inline_keyboard.add(back_button)
    bot.send_message(message.chat.id, f"Запасная часть с ID {spare_part_id} была удалена.", reply_markup=inline_keyboard)


def admin_view_users(message, page):
    users = db.get_users_by_page(page)
    bot.delete_message(message.chat.id, message.id)

    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)


    user_list_message = "Список пользователей:\n"
    for user in users:
        user_button = types.InlineKeyboardButton(f"{user.first_name} --- {user.phone_number}", callback_data=f"admin_user_info_{user.id}")
        delete_button = types.InlineKeyboardButton(f"Удалить", callback_data=f"admin_delete_user_{user.id}_{page}")
        order_button = types.InlineKeyboardButton(f"Заказы", callback_data=f"admin_view_orders_{user.id}_{page}")
        inline_keyboard.add(user_button)
        inline_keyboard.add(order_button, delete_button)

    pagination_buttons = create_pagination_buttons(page, "admin_view_users")
    inline_keyboard.row(*pagination_buttons)
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    inline_keyboard.add(back_button)
    bot.send_message(message.chat.id, user_list_message, reply_markup=inline_keyboard)

def admin_show_orders_by_user(message, user_id, page):
    print(user_id)
    if user_id != 'all':
        user = db.get_user_by_id(user_id)
        orders_message = f"Заказы пользователя {user.first_name}:\n\n"
        orders = db.get_orders_by_user_id_page(user_id, page) 
    else:
        orders_message = "Вот все заказы:\n\n"
        orders = db.get_orders_by_page(page)

    bot.delete_message(message.chat.id, message.id)

    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    for order in orders:
        order_button = types.InlineKeyboardButton(f"Услуга: {order.service_type}\n\nСтатус: {order.status}\n" ,
                                                  callback_data=f"admin_show_order_{order.id}")
        inline_keyboard.add(order_button)

    pagination_buttons = create_pagination_buttons(page, f"admin_view_orders_{user_id}")
    inline_keyboard.row(*pagination_buttons)    
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    inline_keyboard.add(back_button)

    bot.send_message(message.chat.id, orders_message, reply_markup=inline_keyboard)


def admin_delete_user(message, user_id):
    bot.delete_message(message.chat.id, message.id)
    print(user_id)
    user = db.get_user_by_id(user_id)
    db.delete_user_by_id(user_id)
    db.delete_orders_by_user_id(user.telegram_id)
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    inline_keyboard.add(back_button)
    bot.send_message(message.chat.id, f"Пользователь с ID {user_id} и связанные с ним заказы были удалены.", reply_markup=inline_keyboard)

def edit_service(message, service_id):
    service = db.get_service_by_id(service_id)
    service_info_message = f"Услуга : {service.name}\n\nОписание: {service.description}\n\nСредняя стоимость: {service.average_cost}\n\nПредполагаемое время завершения: {service.estimated_completion_time}"
    bot.send_message(message.chat.id, service_info_message)
    bot.send_message(message.chat.id, "Пожалуйста, укажите детали услуги через запятую в следующем формате:\n"
                                            "Название, описание, средняя стоимость, предполагаемое время выполнения")

    bot.register_next_step_handler(message, lambda message: process_edit_service(message, service))


def process_edit_service(message, service):
    updated_details = message.text.split(',')
    if len(updated_details) != 4:
        bot.send_message(message.chat.id, "Пожалуйста, укажите все необходимые поля: Название, Описание, Средняя стоимость, Предполагаемое время выполнения")    
        bot.register_next_step_handler(message, lambda message: process_edit_service(message, service))
        return
    service_id = service.id
    service = tuple(updated_details)
    
    db.update_service(service_id, service)

    bot.send_message(message.chat.id, "Сервис был успешно обновлен.")

    admin_show_service(message, service_id)


def admin_show_service(message ,service_id):
    cid = message.chat.id
    message_id = message.id

    service = db.get_service_by_id(service_id)

    bot.delete_message(cid, message_id)
    service_info_message = f"Услуга : {service.name}\n\nОписание: {service.description}\n\nСредняя стоимость: {service.average_cost}\n\nПредполагаемое время завершения: {service.estimated_completion_time}"
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    back_button = types.InlineKeyboardButton("Назад", callback_data="admin_view_services_1")
    edit_button = types.InlineKeyboardButton(f"Редактировать", callback_data=f"admin_edit_service_{service.id}")
    delete_button = types.InlineKeyboardButton(f"Удалить", callback_data=f"admin_delete_service_{service.id}")
    inline_keyboard.add(edit_button, delete_button)
    inline_keyboard.add(back_button)

    bot.send_message(cid, service_info_message, reply_markup=inline_keyboard)



def view_services(message, page=1):
    bot.delete_message(message.chat.id, message.message_id)
    page = int(page)
    services = db.get_services_by_page(page)
    chat_id = message.chat.id
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    for service in services:
        service_button = types.InlineKeyboardButton(f"{service.name}", callback_data=f"admin_show_service_{service.id}")
        edit_button = types.InlineKeyboardButton(f"Редактировать", callback_data=f"admin_edit_service_{service.id}")
        delete_button = types.InlineKeyboardButton(f"Удалить", callback_data=f"admin_delete_service_{service.id}")
        inline_keyboard.add(service_button)
        inline_keyboard.add(edit_button, delete_button)

    pagination_buttons = create_pagination_buttons(page, "admin_view_services")
    inline_keyboard.row(*pagination_buttons)

    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    inline_keyboard.add(back_button)

    bot.send_message(chat_id, "Вот доступные услуги:", reply_markup=inline_keyboard)

def admin_delete_service(message,service_id):
    db.delete_service_by_id(service_id)
    cid = message.chat.id
    bot.send_message(cid, f"Служба с ID {service_id} была удалена.")
    view_services(message, 1)
    

def add_service(message, user_id):
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "Пожалуйста, укажите детали услуги через запятую в следующем формате:\n"
                                      "Название, описание, средняя стоимость, предполагаемое время выполнения")
    bot.register_next_step_handler(message, process_service_details)


def process_service_details(message):
    service_details = message.text.split(',')

    if len(service_details) != 4:
        bot.send_message(message.chat.id, "Пожалуйста, укажите все необходимые поля: Название, Описание, Средняя стоимость, Предполагаемое время выполнения")
        return

    name, description, average_cost, estimated_completion_time = service_details

    db.save_service((name, description, average_cost, estimated_completion_time))
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    inline_keyboard.add(back_button)

    bot.send_message(message.chat.id, "Услуга успешно добавлена.", reply_markup=inline_keyboard)




def admin_view_spare_parts_menu(mess, page):
    spare_parts = db.get_spare_parts_by_page(page)
    bot.delete_message(mess.chat.id, mess.id)
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    for part in spare_parts:
        part_button = types.InlineKeyboardButton(part.title, callback_data=f"admin_about_spare_part_{part.id}")
        delete_button = types.InlineKeyboardButton("Удалить", callback_data=f"admin_delete_spare_part_{part.id}")
        edit_button = types.InlineKeyboardButton("Редактировать", callback_data=f"admin_edit_spare_part_{part.id}")
        inline_keyboard.add(part_button)
        inline_keyboard.add(delete_button, edit_button)

    pagination_buttons = create_pagination_buttons(page, "admin_view_spare_parts")
    inline_keyboard.row(*pagination_buttons)
    message = "Здесь представлены все запчасти для нашего сервиса."
    back_button = types.InlineKeyboardButton("Назад ", callback_data="back_to_admin_menu")
    inline_keyboard.add(back_button)
    bot.send_message(mess.chat.id, message, reply_markup=inline_keyboard)

    
def show_spare_parts_menu(call):
    part_id = int(call.data.split("_")[-1])
    spare_part = db.get_spare_part_by_id(part_id)
    cid = call.message.chat.id
    bot.delete_message(cid, call.message.message_id)

    part_info_message = f"Запасная часть: {spare_part.title}\n\nОписание: {spare_part.description}\n\nСовместимость: {spare_part.compatibility_info}\n\nPrice: {spare_part.price}\n\nStock Availability: {spare_part.stock_availability}"


    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    back_button = types.InlineKeyboardButton("Назад", callback_data="admin_view_spare_parts_1")
    inline_keyboard.add(back_button)
    bot.send_message(call.message.chat.id, part_info_message, reply_markup=inline_keyboard)

def admin_edit_spare_part(message, spare_id):
    spare_part = db.get_spare_part_by_id(spare_id)
    bot.delete_message(message.chat.id, message.id)
    if not spare_part:
        bot.reply_to(message, "Spare part not found.")
        return

    bot.send_message(message.chat.id, "Пожалуйста, предоставьте обновленную информацию о запчасти через запятую в следующем формате:\n"
                                      "Название, Описание, Цена, Совместимость, Наличие")
    bot.register_next_step_handler(message, process_spare_part_update, spare_id)


def admin_add_spare_part(message):
    bot.delete_message(message.chat.id, message.id)
    bot.send_message(message.chat.id, "Пожалуйста, укажите детали, разделенные запятыми, в следующем формате:\n"
                                      "Название, Описание, Цена, Совместимость, Наличие")

    bot.register_next_step_handler(message, process_spare_part_details)

def process_spare_part_details(message):
    spare_part_details = message.text.split(',')

    if len(spare_part_details) != 5:
        bot.send_message(message.chat.id, "Пожалуйста, укажите детали в правильном формате:\nНазвание, Описание, Цена, Совместимость, Наличие")
        bot.register_next_step_handler(message, process_spare_part_details)
        return

    prince = 0
    try:
        price = float(spare_part_details[2])
    except:
        bot.send_message(message.chat.id, "Пожалуйста, укажите действительную цену.\nЦена должна быть числом")
        bot.register_next_step_handler(message, process_spare_part_details)
        return
    spare_part_details[2] = float(price)

    spare_part_id = db.add_spare_part(tuple(spare_part_details))
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    back_button = types.InlineKeyboardButton("Назад", callback_data="admin_view_spare_parts_1")
    inline_keyboard.add(back_button)
    bot.send_message(message.chat.id, f"Запасная часть '{spare_part_details[0]}' была успешно добавлена!", reply_markup=inline_keyboard)


def process_spare_part_update(message, spare_id):
    updated_details = message.text.split(',')

    expected_field_count = 5 
    if len(updated_details) != expected_field_count:
        bot.send_message(message.chat.id, "Пожалуйста, предоставьте обновленную информацию о запасной части в правильном формате.")
        return

    try:
        db.update_spare_part(spare_id, tuple(updated_details))
        bot.delete_message(message.chat.id, message.id)
        inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
        back_button = types.InlineKeyboardButton("Назад", callback_data="admin_view_spare_parts_1")
        inline_keyboard.add(back_button)
        bot.send_message(message.chat.id, "Запасная часть успешно обновлена.", reply_markup=inline_keyboard)
    except Exception as e:
        bot.send_message(message.chat.id, f"При обновлении запчасти произошла ошибка: {e}")

def admin_faq_button(message ,page):
    bot.delete_message(message.chat.id, message.id)
    faqs = db.get_faqs_by_page(page)
    if not faqs:
        bot.send_message(message.chat.id, "Пока нет доступных вопросов и ответов, введите команду /admin, чтобы вернуться на главное меню")
        return
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    faq_message = "Часто задаваемые вопросы:\n\n"
    # bot.send_message(message.chat.id, faq_message)``
    for num,faq in enumerate(faqs):
        faq_button = types.InlineKeyboardButton(f"{num+1}. {faq.question}", callback_data=f"admin_view_faq_{faq.id}")
        edit_button = types.InlineKeyboardButton(f"Редактировать", callback_data=f"admin_edit_faq_{faq.id}")
        delete_button = types.InlineKeyboardButton(f"Удалить", callback_data=f"admin_delete_faq_{faq.id}")
        inline_keyboard.row(faq_button)
        inline_keyboard.row(edit_button, delete_button)

    pagination_buttons = create_pagination_buttons(page, "admin_faq")
    inline_keyboard.row(*pagination_buttons)
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    inline_keyboard.add(back_button)
    bot.send_message(message.chat.id, faq_message, reply_markup=inline_keyboard,  parse_mode= 'Markdown')


def admin_view_faq(message, faq_id):
    faq = db.get_faq_by_id(faq_id)
    faq_message = f"*{faq.question}*\n"
    faq_message += f"{faq.answer}"
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    edit_button = types.InlineKeyboardButton(f"Редактировать", callback_data=f"admin_edit_faq_{faq.id}")
    delete_button = types.InlineKeyboardButton(f"Удалить", callback_data=f"admin_delete_faq_{faq.id}")
    inline_keyboard.add(edit_button, delete_button)
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    inline_keyboard.add(back_button)
    bot.send_message(message.chat.id, faq_message, reply_markup=inline_keyboard,  parse_mode= 'Markdown')
    bot.delete_message(message.chat.id, message.id)


def admin_edit_faq(message, faq_id):
    faq = db.get_faq_by_id(faq_id)
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2) 
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    inline_keyboard.add(back_button)
    if faq:
        prompt_message = f"Редактирование FAQ (ID: {faq_id})\n\nТекущий вопрос: {faq.question}\nТекущий ответ: {faq.answer}\n\nОтправьте новый вопрос и ответ через запятую (Например: 'Новый вопрос, Новый ответ'):"
        bot.send_message(message.chat.id, prompt_message, reply_markup=inline_keyboard)
        bot.register_next_step_handler(message, process_edit_faq, faq)
    else:
        error_message = "Ошибка: FAQ с указанным ID не найден."
        bot.send_message(message.chat.id, error_message, reply_markup=inline_keyboard)
    bot.delete_message(message.chat.id, message.id)


def process_edit_faq(message, current_faq):
    new_question, new_answer = map(str.strip, message.text.split(','))

    current_faq.question = new_question
    current_faq.answer = new_answer

    db.update_faq(current_faq)

    confirmation_message = f"FAQ (ID: {current_faq.id}) успешно обновлен.\n\nНовый вопрос: {new_question}\nНовый ответ: {new_answer}"
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2) 
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    inline_keyboard.add(back_button)
    bot.send_message(message.chat.id, confirmation_message, reply_markup=inline_keyboard)


def admin_delete_faq(message, faq_id):
    db.delete_faq(faq_id)
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    inline_keyboard.add(back_button)
    bot.delete_message(message.chat.id, message.id)
    bot.send_message(message.chat.id, f"FAQ с id {faq_id} удален", reply_markup=inline_keyboard)


def add_faq_button_handler(message):
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    back_button = types.InlineKeyboardButton("Отменить", callback_data="back_to_admin_menu")
    inline_keyboard.add(back_button)
    bot.delete_message(message.chat.id, message.id)
    bot.send_message(message.chat.id, "Пожалуйста, укажите вопрос для нового FAQ:", reply_markup=inline_keyboard)
    bot.register_next_step_handler(message, process_new_faq_question)


def process_new_faq_question(message):
    faq_data = [message.text]
    bot.send_message(message.chat.id, "Пожалуйста, дайте ответ на новый FAQ:")
    bot.register_next_step_handler(message, process_new_faq_answer, faq_data)


def process_new_faq_answer(message, faq_data):
    faq_data.append(message.text)
    db.create_faq(faq_data[0], faq_data[1])
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    inline_keyboard.add(back_button)
    bot.send_message(message.chat.id, "Спасибо! Новый FAQ успешно добавлен.", reply_markup=inline_keyboard)



def admin_check_messages(message):
    if message.chat.id not in ADMIN_IDS:
        inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
        back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
        bot.send_message(message.chat.id, "У вас нет разрешения на использование этой команды", reply_markup=inline_keyboard)
        return
    messages = db.get_messages_by_status("Отвечено", invert=True)
    bot.delete_message(message.chat.id, message.id)

    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    if messages:
        for sp_message in messages:
            sp_message_button = types.InlineKeyboardButton(f"ID сообщения: {sp_message.id}\nПользователь: {sp_message.user_id}", callback_data=f"see_user_message_{sp_message.id}")
            inline_keyboard.add(sp_message_button)

    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    inline_keyboard.add(back_button)

    bot.send_message(message.chat.id, "Вот все сообщения без ответа:", reply_markup=inline_keyboard)


def admin_show_feedbacks(message, page):
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)

    feedbacks = db.get_feedbacks_by_page(page)
    bot.delete_message(message.chat.id, message.message_id)
    if not feedbacks:
        back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
        inline_keyboard.add(back_button)
        bot.send_message(message.chat.id, "Пока нет отзывов", reply_markup=inline_keyboard)
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
    # leave_feedback_button = types.InlineKeyboardButton("Оставить отзыв", callback_data="leave_feedback")
    # inline_keyboard.row(leave_feedback_button)
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    inline_keyboard.add(back_button)
    bot.send_message(message.chat.id, feedback_message, reply_markup=inline_keyboard)




def create_admin_menu():
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    view_orders_button = types.InlineKeyboardButton("Смотреть заказы", callback_data="admin_view_orders_all_1")
    archive_button = types.InlineKeyboardButton("Архив заказов", callback_data="admin_view_archived_orders_1")
    view_users_button = types.InlineKeyboardButton("Пользователи", callback_data="admin_view_users_1")
    add_service_button = types.InlineKeyboardButton("Добавить услугу", callback_data="admin_add_service")
    delete_service_button = types.InlineKeyboardButton("Посмотреть услуги", callback_data="admin_view_services_1")
    add_spare_part_button = types.InlineKeyboardButton("Добавить запчасть", callback_data="admin_add_spare_part")
    view_spare_parts = types.InlineKeyboardButton("Запчасти", callback_data="admin_view_spare_parts_1")
    faq_button = types.InlineKeyboardButton("FAQ", callback_data="admin_faq_1")
    feedback_button = types.InlineKeyboardButton("Оценки и отзывы", callback_data="admin_show_feedbacks_1")
    add_faq_button = types.InlineKeyboardButton("Добавить FAQ", callback_data="admin_add_faq")
    support_messages = types.InlineKeyboardButton("Сообщения в службу поддержки", callback_data="admin_support_messages")
    inline_keyboard.add(
        view_orders_button, view_users_button, archive_button ,
        add_service_button, delete_service_button,
        add_spare_part_button, view_spare_parts,
        faq_button, feedback_button,add_faq_button
    )
    inline_keyboard.add(support_messages)
    return inline_keyboard


