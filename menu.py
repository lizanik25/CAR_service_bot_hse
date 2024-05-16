from telebot import types
from database import db

def create_main_menu():
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    func_button = types.InlineKeyboardButton("Просмотр заказов", callback_data="view_orders")
    service_button = types.InlineKeyboardButton("Услуги", callback_data="show_services")
    create_order_button = types.InlineKeyboardButton("Создать заказ", callback_data="create_order")
    spare_parts_button = types.InlineKeyboardButton("Запчасти", callback_data="show_spare_parts")
    feedback_button = types.InlineKeyboardButton("Оценки и отзывы", callback_data="show_feedbacks_1")
    support = types.InlineKeyboardButton("Техническая поддержка", callback_data="tech_support")
    faq_button = types.InlineKeyboardButton("FAQ", callback_data="faq_1")
    edit_profile = types.InlineKeyboardButton("Отредактировать профиль", callback_data="edit_profile")
    

    inline_keyboard.add(service_button, spare_parts_button, func_button, feedback_button,support, faq_button)

    inline_keyboard.add(edit_profile)
    inline_keyboard.add(create_order_button)
    return inline_keyboard



def create_services_menu(page):
    services = db.get_services_by_page(page)

    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    for service in services:
        service_button = types.InlineKeyboardButton(service.name, callback_data=f"show_service_{service.id}")
        inline_keyboard.add(service_button)

    pagination_buttons = create_pagination_buttons(page, "show_services")
    inline_keyboard.row(*pagination_buttons)

    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard.add(back_button)

    return inline_keyboard

def create_spare_parts_menu(page):
    spare_parts = db.get_spare_parts_by_page(page)

    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    for part in spare_parts:
        part_button = types.InlineKeyboardButton(part.title, callback_data=f"about_spare_part_{part.id}")
        inline_keyboard.add(part_button)

    pagination_buttons = create_pagination_buttons(page, "show_spare_parts")
    inline_keyboard.row(*pagination_buttons)

    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard.add(back_button)

    return inline_keyboard

def create_view_orders_menu(user_id, page):
    orders = db.get_orders_by_user_id_page(user_id, page)

    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    for order in orders:
        order_button = types.InlineKeyboardButton(f"Услуга: {order.service_type}\n\nСтатус: {order.status}\n" ,
                                                  callback_data=f"show_order_{order.id}")
        inline_keyboard.add(order_button)

    pagination_buttons = create_pagination_buttons(page, f"{user_id}")
    inline_keyboard.row(*pagination_buttons)

    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_main")
    inline_keyboard.add(back_button)

    return inline_keyboard


def create_pagination_buttons(page, menu_type):
    page_count = 0
    if menu_type == 'show_spare_parts':
        page_count = db.get_page_count('spare_parts')
    elif menu_type.isdigit():
        page_count = db.get_user_order_page_count(int(menu_type))
        menu_type = "view_orders"
    elif menu_type == "admin_view_users":
        page_count = db.get_users_page_count()
    elif menu_type == "admin_view_services":
        page_count = db.get_page_count('services')
    elif menu_type.startswith("admin_view_orders"): 
        try:
            user_id = int(menu_type.split("_")[-1])
            page_count = db.get_user_order_page_count(user_id)
        except:
            page_count = db.get_orders_page_count()
    elif menu_type == "admin_view_spare_parts":
        page_count = db.get_page_count('spare_parts')
    elif menu_type == "show_feedbacks":
        page_count = db.get_feedback_count_all_users()
    elif menu_type == "faq":
        page_count = db.get_faq_page_count()    
    elif menu_type == "admin_faq":
        page_count = db.get_faq_page_count()   
    elif menu_type == "admin_view_archived_orders":
        page_count = db.get_orders_page_count()   
    elif menu_type.startswith("see_messages"):
        splited_menu = menu_type.split("_")
        user_id = int(splited_menu[-1])
        menu_type = splited_menu[0] + "_" + splited_menu[1]
        page_count = db.get_user_messages_page_count(user_id)
    else:
        page_count = db.get_page_count('services')
    print(menu_type, "menu type")
    prev_button = types.InlineKeyboardButton(f"◀️ Предыдущая {max(1, page-1)}", callback_data=f"{menu_type}_{max(1, page-1)}")
    current = types.InlineKeyboardButton(f"{page}/{page_count}", callback_data=f"x")
    next_button = types.InlineKeyboardButton(f"Следующая {min(page_count, page + 1)}▶️", callback_data=f"{menu_type}_{min(page_count, page + 1)}")
    return [prev_button , current, next_button]



