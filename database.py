import sqlite3
from config import DATABASE_NAME
from models import User, Order, Service, SparePart, Feedback, FAQ, Message_to_support, Busy_slots
from datetime import datetime
import random
class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
        self.cur = self.conn.cursor()

    def create_tables(self):
        # Create necessary tables if they don't exist
        self.cur.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            first_name TEXT,
                            last_name TEXT,
                            phone_number TEXT,
                            telegram_id INTEGER,
                            registration_date TEXT,
                            activity_status TEXT,
                            email TEXT
                            )''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS orders (
                            id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            vehicle_registration TEXT,
                            make TEXT,
                            model TEXT,
                            year_of_issue TEXT,
                            service_type TEXT,
                            service_cost REAL,
                            creation_date TEXT,
                            planned_date TEXT,
                            planned_time TEXT,
                            buys_consumables TEXT,
                            status TEXT,
                            comments TEXT,
                            FOREIGN KEY (user_id) REFERENCES users(id)
                            )''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS services (
                            id INTEGER PRIMARY KEY,
                            name TEXT,
                            description TEXT,
                            average_cost REAL,
                            estimated_completion_time TEXT
                            )''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS spare_parts (
                            id INTEGER PRIMARY KEY,
                            title TEXT,
                            description TEXT,
                            compatibility_info TEXT,
                            price REAL,
                            stock_availability TEXT
                            )''')
        
        self.cur.execute('''CREATE TABLE IF NOT EXISTS feedback (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            text TEXT,
                            rating INTEGER,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS FAQ (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            question TEXT,
                            answer TEXT
                            )''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS messages_to_support (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            message TEXT,
                            user_id INTEGER,
                            status TEXT,
                            sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS busy_slots (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            date TEXT,
                            busy_times TEXT
                            )''')
        # Create more tables as needed
    def add_busy_slots(self, date, busy_times):
        self.cur.execute('''INSERT INTO busy_slots (date, busy_times) VALUES (?, ?)''', (date, busy_times))
        self.conn.commit()
    
    def update_user_field(self, user_id, field_name, new_value):
        # Update the specified field for the user with the new value
        query = f"UPDATE users SET {field_name} = ? WHERE telegram_id = ?"
        params = (new_value, user_id)
        self.cur.execute(query, params)
        self.conn.commit()

    def get_order_comments(self, order_id):
        query = "SELECT comments FROM orders WHERE id = ?"
        self.cur.execute(query, (order_id,))
        result = self.cur.fetchone()
        if result:
            return result[0]
        else:
            return None

    def order_add_comment(self, order_id, comment):
        # Retrieve existing comments for the order
        existing_comments = self.get_order_comments(order_id)
        
        # Append the new comment to the existing comments
        updated_comments = existing_comments + "\n\n" + comment
        
        # Update the order with the updated comments
        query = "UPDATE orders SET comments = ? WHERE id = ?"
        params = (updated_comments, order_id)
        self.cur.execute(query, params)
        self.conn.commit()


    def get_all_orders(self):
        sql = 'SELECT * FROM orders'
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        if rows:
            return [Order(*row) for row in rows]
        return []

    def get_or_create_busy_slots(self, date):
        # Check if an entry for the given date already exists
        self.cur.execute('''SELECT * FROM busy_slots WHERE date = ?''', (date,))
        row = self.cur.fetchone()

        if row:
            # Entry exists, return busy times
            return Busy_slots(*row)
        else:
            # Entry does not exist, create a new one
            self.cur.execute('''INSERT INTO busy_slots (date, busy_times) VALUES (?, ?)''', (date, '[]'))
            self.conn.commit()
            # Fetch the newly created row
            self.cur.execute('''SELECT * FROM busy_slots WHERE date = ?''', (date,))
            new_row = self.cur.fetchone()
            return Busy_slots(*new_row)

    def get_messages_by_status(self, status, invert=False):
        # Query the database to get messages by status
        if not invert:
            query = "SELECT * FROM messages_to_support WHERE status = ?"
        else:
            query = "SELECT * FROM messages_to_support WHERE status != ?"
        params = (status,)
        self.cur.execute(query, params)
        rows = self.cur.fetchall()
        if rows:
            return [Message_to_support(*row) for row in rows]
        return None


    def update_busy_slot(self, date, busy_times):
        self.cur.execute('''UPDATE busy_slots SET busy_times = ? WHERE date = ?''', (busy_times, date))
        self.conn.commit()

    def change_message_status(self, message_id, new_status):
            query = "UPDATE messages_to_support SET status = ? WHERE id = ?"
            self.cur.execute(query, (new_status, message_id))
            self.conn.commit()

    def insert_message_to_support(self, message, user_id):
        query = "INSERT INTO messages_to_support (message, user_id, status) VALUES (?, ?, ?)"
        self.cur.execute(query, (message, user_id, "В ожидании"))  # Status set to Pending by default
        self.conn.commit()
        return self.cur.lastrowid

    def delete_message_from_support(self, message_id):
        query = "DELETE FROM messages_to_support WHERE id = ?"
        self.cur.execute(query, (message_id,))
        self.conn.commit()

    def get_messages_by_user_id(self, user_id):
        query = "SELECT * FROM messages_to_support WHERE user_id = ?"
        self.cur.execute(query, (user_id,))
        return self.cur.fetchall()

    def get_messages_by_page(self, page_num, page_size=5):
        offset = (page_num - 1) * page_size
        query = "SELECT * FROM messages_to_support ORDER BY sent DESC LIMIT ? OFFSET ?"
        params = (page_size, offset)
        self.cur.execute(query, params)
        rows = self.cur.fetchall()
        if rows:
            return [Message_to_support(*row) for row in rows]
        return None
    
    
    def get_message_by_id(self, message_id):
        query = "SELECT * FROM messages_to_support WHERE id = ?"
        self.cur.execute(query, (message_id,))
        row = self.cur.fetchone()
        if row:
            return Message_to_support(*row)
        return None

    def get_all_messages(self):
        query = "SELECT * FROM messages_to_support"
        self.cur.execute(query)
        rows = self.cur.fetchall()
        if rows:
            return [Message_to_support(*row) for row in rows]
        return None

    def get_messages_by_user_id_and_page(self, user_id, page_num, page_size=5):
        offset = (page_num - 1) * page_size
        query = "SELECT * FROM messages_to_support WHERE user_id = ? ORDER BY sent DESC LIMIT ? OFFSET ?"
        params = (user_id, page_size, offset)
        self.cur.execute(query, params)
        rows = self.cur.fetchall()
        if rows:
            return [Message_to_support(*row) for row in rows]
        return None
    
    def get_faq_by_id(self, faq_id):
        # Query the database to retrieve the FAQ with the given ID
        query = "SELECT * FROM FAQ WHERE id = ?"
        self.cur.execute(query, (faq_id,))
        faq_row = self.cur.fetchone()
        if faq_row:
            faq = FAQ(*faq_row)
            return faq
        else:
            return None
    def get_messages_by_status_and_user_id(self, status, user_id):
        query = "SELECT * FROM messages_to_support WHERE status = ? AND user_id = ? ORDER BY sent DESC"
        self.cur.execute(query, (status, user_id))
        rows = self.cur.fetchall()
        if rows:
            return [Message_to_support(*row) for row in rows]
        return None

    def get_user_messages_page_count(self, user_id, per_page=5):
        total_messages = self.get_user_messages_count(user_id)
        page_count = (total_messages + per_page - 1) // per_page
        return page_count
    
    def get_all_messages_count(self):
        query = "SELECT COUNT(*) FROM messages_to_support"
        self.cur.execute(query)
        count = self.cur.fetchone()[0]
        return count
    
    def get_user_messages_count(self, user_id):
        query = "SELECT COUNT(*) FROM messages_to_support WHERE user_id = ?"
        self.cur.execute(query, (user_id,))
        count = self.cur.fetchone()[0]
        return count

    def get_all_messages_page_count(self, per_page=5):
        total_messages = self.get_all_messages_count()
        page_count = (total_messages + per_page - 1) // per_page
        return page_count






    def create_faq(self, question, answer):
        query = "INSERT INTO FAQ (question, answer) VALUES (?, ?)"
        self.cur.execute(query, (question, answer))
        self.conn.commit()

    def update_faq(self, faq):
        query = "UPDATE FAQ SET question = ?, answer = ? WHERE id = ?"
        self.cur.execute(query, (faq.question, faq.answer, faq.id))
        self.conn.commit()

    def delete_faq(self, id):
        query = "DELETE FROM FAQ WHERE id = ?"
        self.cur.execute(query, (id,))
        self.conn.commit()

    def get_faqs_by_page(self, page, per_page=5):
        offset = (page - 1) * per_page
        query = "SELECT * FROM FAQ LIMIT ? OFFSET ?"
        self.cur.execute(query, (per_page, offset))
        rows = self.cur.fetchall()
        if rows:
            return [FAQ(*row) for row in rows]
        return None


    def insert_feedback(self, user_id, text, rating):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = 'INSERT INTO feedback (user_id, text, rating, timestamp) VALUES (?, ?, ?, ?)'
        self.cur.execute(sql, (user_id, text, rating, timestamp,))
        self.conn.commit()

    def get_all_feedback(self):
        sql = 'SELECT * FROM feedback'
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        if rows:
            return [Feedback(*row) for row in rows]
        return None

    def get_feedback_by_user_id(self, user_id):
        sql = 'SELECT * FROM feedback WHERE user_id = ?'
        self.cur.execute(sql, (user_id,))
        rows = self.cur.fetchall()
        if rows:
            return [Feedback(*row) for row in rows]
        return None

    def delete_feedback_by_id(self, feedback_id):
        sql = 'DELETE FROM feedback WHERE id = ?'
        self.cur.execute(sql, (feedback_id,))
        self.conn.commit()

    def get_feedbacks_by_user_id(self, user_id):
        sql = 'SELECT * FROM feedback WHERE user_id = ?'
        self.cur.execute(sql, (user_id,))
        rows = self.cur.fetchall()
        if rows:
            return [Feedback(*row) for row in rows]
        return None
    
    def get_feedbacks_by_page(self, page, per_page=5):
        offset = (page - 1) * per_page
        sql = 'SELECT * FROM feedback LIMIT ? OFFSET ?'
        self.cur.execute(sql, (per_page, offset))
        rows = self.cur.fetchall()
        # print(rows, rows)
        if rows:
            return [Feedback(*row) for row in rows]
        return None

    def get_feedback_count_all_users(self, per_page=5):
        sql = 'SELECT COUNT(*) FROM feedback'
        self.cur.execute(sql)
        total_feedbacks = self.cur.fetchone()[0]
        # print(total_feedbacks)
        page_count = (total_feedbacks + per_page - 1) // per_page
        # print(page_count, "rows")
        return page_count

    def get_feedback_count_by_user_id(self, user_id):
        sql = 'SELECT COUNT(*) FROM feedback WHERE user_id = ?'
        self.cur.execute(sql, (user_id,))
        count = self.cur.fetchone()[0]
        return count

    def get_faq_page_count(self, per_page=5):
        query = "SELECT COUNT(*) FROM FAQ"
        self.cur.execute(query)
        total_faqs = self.cur.fetchone()[0]
        page_count = (total_faqs + per_page - 1) // per_page
        return page_count


    def add_user(self, data):
        # Add a new user to the database
        self.cur.execute('''INSERT INTO users (first_name, last_name, phone_number, telegram_id, registration_date, activity_status, email) 
                            VALUES (?, ?, ?, ?, ?, ?, ?)''', data)
        self.conn.commit()
    def delete_spare_part_by_id(self, spare_id):
        try:
            self.cur.execute('''DELETE FROM spare_parts WHERE id = ?''', (spare_id,))
            self.conn.commit()
        except Exception as e:
            print(f"An error occurred while deleting spare part with ID {spare_id}: {e}")
            self.conn.rollback()

    def delete_user_by_id(self, user_id):
        # Delete the user from the database
        self.cur.execute('''DELETE FROM users WHERE id = ?''', (user_id,))
        self.conn.commit()

    def get_user_by_id(self, user_id):
        self.cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = self.cur.fetchone()
        if row:
            return User(*row)
        return None


    def get_user_by_telegram_id(self, telegram_id):
        # Retrieve a user by Telegram ID
        self.cur.execute('''SELECT * FROM users WHERE telegram_id = ?''', (telegram_id,))
        row = self.cur.fetchone()
        if row:
            return User(*row)
        return None

    def update_user_activity_status(self, telegram_id, activity_status):
        # Update user activity status
        self.cur.execute('''UPDATE users SET activity_status = ? WHERE telegram_id = ?''', (activity_status, telegram_id))
        self.conn.commit()

    def add_order(self, data):
        # Add a new order to the database
        self.cur.execute('''INSERT INTO orders (user_id, vehicle_registration, make, model, year_of_issue, service_type, service_cost, 
                            creation_date, planned_date, planned_time, buys_consumables, status, comments) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
        self.conn.commit()

    def save_order_details(self, order_details):
            # Extract order details from the order_details dictionary
            data = (
                order_details["user_id"],
                order_details["vehicle_registration"],
                order_details["make"],
                order_details["model"],
                order_details["year_of_issue"],
                order_details["service_type"],
                order_details["service_cost"],
                order_details["creation_date"],
                order_details["planned_date"],
                order_details["planned_time"],
                order_details["buys_consumables"],
                order_details.get("status", "В ожидании"),  # Default status is 'pending'
                order_details["additional_details"]
            )

            # Save the order details using the add_order method
            self.add_order(data)
        
    def get_orders_by_user_id(self, user_id):
        # Retrieve orders by user ID
        self.cur.execute('''SELECT * FROM orders WHERE user_id = ?''', (user_id,))
        rows = self.cur.fetchall()
        if rows:
            return [Order(*row) for row in rows]
        return []

    def get_users_by_page(self, page_num, page_size=5):
        offset = (page_num - 1) * page_size
        query = "SELECT * FROM users LIMIT ? OFFSET ?"
        params = (page_size, offset)
        self.cur.execute(query, params)
        rows = self.cur.fetchall()
        if rows:
            return [User(*row) for row in rows]
        return []

    def get_users_count(self):
        query = "SELECT COUNT(*) FROM users"
        self.cur.execute(query)
        count = self.cur.fetchone()[0]
        return count
    
    def get_users_page_count(self, per_page=5):
        query = "SELECT COUNT(*) FROM users"
        self.cur.execute(query)
        total_users = self.cur.fetchone()[0]
        page_count = (total_users + per_page - 1) // per_page
        return page_count

    def update_order_status(self, order_id, status):
        # Update order status
        self.cur.execute('''UPDATE orders SET status = ? WHERE id = ?''', (status, order_id))
        self.conn.commit()

    def update_order_comments(self, order_id, comments):
        # Update order comments
        self.cur.execute('''UPDATE orders SET comments = ? WHERE id = ?''', (comments, order_id))
        self.conn.commit()

    def delete_order(self, order_id):
        # Delete order
        self.cur.execute('''DELETE FROM orders WHERE id = ?''', (order_id,))
        self.conn.commit()

    def delete_orders_by_user_id(self, user_id):
        # Delete orders associated with the specified user ID
        self.cur.execute('''DELETE FROM orders WHERE user_id = ?''', (user_id,))
        self.conn.commit()

    def add_service(self, data):
        # Add a new service to the database
        self.cur.execute('''INSERT INTO services (name, description, average_cost, estimated_completion_time) 
                            VALUES (?, ?, ?, ?)''', data)
        self.conn.commit()

    def get_all_services(self):
        # Retrieve all services
        self.cur.execute('''SELECT * FROM services''')
        rows = self.cur.fetchall()
        if rows:
            return [Service(*row) for row in rows]
        return []

    def get_service_by_id(self, service_id):
        # Retrieve a service by ID
        self.cur.execute('''SELECT * FROM services WHERE id = ?''', (service_id,))
        row = self.cur.fetchone()
        if row:
            return Service(*row)
        return None

    def update_service(self, service_id, data):
        # Update service details
        self.cur.execute('''UPDATE services SET name = ?, description = ?, average_cost = ?, 
                            estimated_completion_time = ? WHERE id = ?''', (*data, service_id))
        self.conn.commit()

    def delete_service_by_id(self, service_id):
        # Delete service
        self.cur.execute('''DELETE FROM services WHERE id = ?''', (service_id,))
        self.conn.commit()

    # CRUD functions for spare parts
    def add_spare_part(self, data):
        # Add a new spare part to the database
        self.cur.execute('''INSERT INTO spare_parts (title, description, compatibility_info, price, stock_availability) 
                            VALUES (?, ?, ?, ?, ?)''', data)
        self.conn.commit()
    def save_service(self,data):
        self.cur.execute('''INSERT INTO services (name, description, average_cost, estimated_completion_time) 
                            VALUES (?, ?, ?, ?)''', data)
        self.conn.commit()
    def get_all_spare_parts(self):
        # Retrieve all spare parts
        self.cur.execute('''SELECT * FROM spare_parts''')
        rows = self.cur.fetchall()
        if rows:
            return [SparePart(*row) for row in rows]
        return []

    def get_spare_part_by_id(self, spare_part_id):
        # Retrieve a spare part by ID
        self.cur.execute('''SELECT * FROM spare_parts WHERE id = ?''', (spare_part_id,))
        row = self.cur.fetchone()
        if row:
            return SparePart(*row)
        return None

    def update_spare_part(self, spare_part_id, data):
        # Update spare part details
        self.cur.execute('''UPDATE spare_parts SET title = ?, description = ?, price = ?,  compatibility_info = ?, 
                            stock_availability = ? WHERE id = ?''', (*data, spare_part_id))
        self.conn.commit()

    def delete_spare_part(self, spare_part_id):
        # Delete spare part
        self.cur.execute('''DELETE FROM spare_parts WHERE id = ?''', (spare_part_id,))
        self.conn.commit()

    def get_order_by_id(self, order_id):
        # Retrieve an order by ID
        self.cur.execute('''SELECT * FROM orders WHERE id = ?''', (order_id,))
        row = self.cur.fetchone()
        if row:
            return Order(*row)
        return None
    
    def delete_order_by_id(self, order_id):
        # Delete an order by ID
        self.cur.execute('''DELETE FROM orders WHERE id = ?''', (order_id,))
        self.conn.commit()

    def get_services_by_page(self, page, per_page=5):
        # Fetch services from the database based on the current page
        offset = (page - 1) * per_page
        self.cur.execute('''SELECT * FROM services LIMIT ? OFFSET ?''', (per_page, offset))
        rows = self.cur.fetchall()
        if rows:
            return [Service(*row) for row in rows]
        return []
    
    def get_spare_parts_by_page(self, page, per_page=5):
        # Fetch spare parts from the database based on the current page
        offset = (page - 1) * per_page
        self.cur.execute('''SELECT * FROM spare_parts LIMIT ? OFFSET ?''', (per_page, offset))
        rows = self.cur.fetchall()
        if rows:
            return [SparePart(*row) for row in rows]
        return []
    
    def get_orders_by_user_id_page(self, user_id, page_num, page_size=3):
        offset = (page_num - 1) * page_size
        query = f"SELECT * FROM orders WHERE user_id = ? LIMIT ? OFFSET ?"
        params = (user_id, page_size, offset)
        self.cur.execute(query, params)
        rows = self.cur.fetchall()
        if rows:
            return [Order(*row) for row in rows]
        return []
    
    def get_orders_page_count(self, per_page=3):
        self.cur.execute("SELECT COUNT(*) FROM orders")
        total_orders_count = self.cur.fetchone()[0]
        page_count = (total_orders_count + per_page - 1) // per_page
        return page_count
    def get_orders_by_page(self, page, per_page=3):
        offset = (page - 1) * per_page
        query = "SELECT * FROM orders LIMIT ? OFFSET ?"
        params = (per_page, offset)
        self.cur.execute(query, params)
        rows = self.cur.fetchall()
        if rows:
            return [Order(*row) for row in rows]
        return []


    def get_user_order_page_count(self, user_id, per_page=3):
        # Get the total number of orders for a specific user
        query = "SELECT COUNT(*) FROM orders WHERE user_id = ?"
        self.cur.execute(query, (user_id,))
        count = self.cur.fetchone()[0]
        page_count = (count + per_page - 1) // per_page
        return page_count


    def get_page_count(self, table_name, per_page=5):
        # Count the total number of rows in the table
        self.cur.execute(f'SELECT COUNT(*) FROM {table_name}')
        total_rows = self.cur.fetchone()[0]
        page_count = (total_rows + per_page - 1) // per_page

        return page_count
    
    def populate_services_table(self):
        # Add initial services to the database
        initial_services = [
            ("Диагностика шасси", "Проведите диагностику системы шасси", 100.00, "2 часа"),
            ("Диагностика двигателя", "Проведение диагностики системы двигателя", 120.00, "3 часа"),
            ("Техническое обслуживание автомобиля", "Текущее обслуживание, включая замену масла и фильтров", 150.00, "4 часа"),
            ("Работа с кондиционером", "Ремонт и обслуживание системы кондиционирования", 80.00, "1 час"),
            ("Замена роликов", "Замена изношенных роликов", 50.00, "30 минут"),
            ("Ремонт и обслуживание генератора", "Ремонт и обслуживание генератора", 200.00, "5 часов"),
            ("Ремонт и обслуживание насоса системы охлаждения", "Ремонт и обслуживание насоса системы охлаждения", 90.00, "2.5 часа"),
            ("Диагностика электрооборудования", "Диагностика ошибок электросистемы с помощью декодера", 110.00, "2 часа"),
            ("Шиномонтаж и балансировка", "Монтаж и балансировка шин", 70.00, "1.5 часа"),
            ("Сварочные работы", "Различные сварочные работы", 80.00, "2 часа")
        ]

        for service_data in initial_services:
            self.cur.execute('''INSERT INTO services (name, description, average_cost, estimated_completion_time) 
                                VALUES (?, ?, ?, ?)''', service_data)
    def populate_spare_parts_table(self):
        # Add initial spare parts to the database
        initial_spare_parts = [
            ("Тормозные колодки", "Сменные тормозные колодки для различных моделей автомобилей", "Совместимо с моделями A, B, C", 50.00, "На складе"),
            ("Масляный фильтр", "Сменный масляный фильтр для регулярного обслуживания", "Совместим с моделями X, Y, Z", 10.00, "На складе"),
            ("Воздушный фильтр", "Сменный воздушный фильтр для регулярного технического обслуживания", "Совместим с моделями X, Y, Z", 15.00, "Есть на складе"),
            ("Свечи зажигания", "Сменные свечи зажигания для обслуживания двигателя", "Совместимо с моделями A, B, C", 8.00, "На складе"),
            ("Лампочки для фар", "Запасные лампочки для фар", "Совместимо с моделями X, Y, Z", 12.00, "В наличии"),
            ("Стеклоочистители", "Замена стеклоочистителей", "Совместимо с моделями A, B, C", 20.00, "На складе"),
            ("Аккумулятор", "Запасной аккумулятор для различных моделей автомобилей", "Совместим с моделями X, Y, Z", 100.00, "В наличии"),
            ("Радиатор", "Сменный радиатор для системы охлаждения двигателя", "Совместим с моделями A, B, C", 80.00, "На складе"),
            ("Топливный насос", "Замена топливного насоса", "Совместим с моделями X, Y, Z", 60.00, "На складе"),
            ("Ремень ГРМ", "Замена ремня ГРМ для обслуживания двигателя", "Совместим с моделями A, B, C", 30.00, "Есть на складе")
        ]

        for part_data in initial_spare_parts:
            self.cur.execute('''INSERT INTO spare_parts (title, description, compatibility_info, price, stock_availability) 
                                VALUES (?, ?, ?, ?, ?)''', part_data)


    def populate_users_table(self):
        # Sample data for users
        users_data = [
            (4, 'Bob', 'Williams', '+222222222', 222222, '2024-01-04', 'active'),
            (5, 'Charlie', 'Brown', '+333333333', 333333, '2024-01-05', 'active'),
            (6, 'Eva', 'Martinez', '+444444444', 444444, '2024-01-06', 'active'),
            (7, 'David', 'Lee', '+555555555', 555555, '2024-01-07', 'active'),
            (8, 'Grace', 'Taylor', '+666666666', 666666, '2024-01-08', 'active'),
            (9, 'Frank', 'Nguyen', '+777777777', 777777, '2024-01-09', 'active'),
            (10, 'Hannah', 'Garcia', '+888888888', 888888, '2024-01-10', 'active'),
            (11, 'Isaac', 'Chen', '+999999999', 999999, '2024-01-11', 'active'),
            (12, 'Julia', 'Lopez', '+101010101', 101010, '2024-01-12', 'active'),
        ]
        
        # SQL statement to insert data into users table
        query = "INSERT INTO users (id, first_name, last_name, phone_number, telegram_id, registration_date, activity_status) VALUES (?, ?, ?, ?, ?, ?, ?)"
        
        # Execute the SQL statement for each user data
        for user_data in users_data:
            self.cur.execute(query, user_data)
        
        # Commit the transaction to save changes
        self.conn.commit()

    def get_all_user_ids(self):
        self.cur.execute('SELECT telegram_id FROM users')
        rows = self.cur.fetchall()
        return [row[0] for row in rows]

    def create_feedback(self, user_id):
        text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        rating = random.randint(1, 5)  # Random rating between 1 and 5
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = 'INSERT INTO feedback (user_id, text, rating, timestamp) VALUES (?, ?, ?, ?)'
        self.cur.execute(sql, (user_id, text, rating, timestamp))
        self.conn.commit()

    def populate_faq(self):
        faqs = [
            ("Как мне записаться на прием?", "Вы можете записаться на прием..."),
            ("Какие способы оплаты вы принимаете?", "Мы принимаем наличные, кредитные/дебетовые карты и онлайн-платежи"),
            ("Какие у вас часы работы?", "Наши часы работы с 9:00 до 18:00 с понедельника по пятницу"),
            ("Даете ли вы гарантию на свои услуги?", "Да, мы предоставляем гарантию 6 месяцев на все наши услуги."),
            ("Могу ли я отменить встречу?", "Да, вы можете отменить встречу, обратившись в нашу службу поддержки."),
            ("Сколько времени занимает стандартная услуга?", "Продолжительность услуги зависит от типа требуемой услуги."),
            ("Оказываете ли вы помощь на дороге?", "Да, мы предлагаем помощь на дороге в экстренных случаях."),
            # Add more FAQ entries as needed
        ]

        for faq in faqs:
            self.create_faq(*faq)
    def populate_feedbacks(self):
        user_ids = self.get_all_user_ids()
        for user_id in user_ids:
            self.create_feedback(user_id) 
# Initialize Database object
db = Database()
