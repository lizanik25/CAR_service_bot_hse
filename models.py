# Define data models
class User:
    def __init__(self, id, first_name, last_name, phone_number, telegram_id, registration_date, activity_status, email):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.telegram_id = telegram_id
        self.registration_date = registration_date
        self.activity_status = activity_status
        self.email = email

class Order:
    def __init__(self, id, user_id, vehicle_registration, make, model, year_of_issue, service_type, service_cost, creation_date, planned_date, planned_time, buys_consumables, status, comments):
        self.id = id
        self.user_id = user_id
        self.vehicle_registration = vehicle_registration
        self.make = make
        self.model = model
        self.year_of_issue = year_of_issue
        self.service_type = service_type
        self.service_cost = service_cost
        self.creation_date = creation_date
        self.planned_date = planned_date
        self.planned_time = planned_time
        self.buys_consumables = buys_consumables
        self.status = status
        self.comments = comments

class Service:
    def __init__(self, id, name, description, average_cost, estimated_completion_time):
        self.id = id
        self.name = name
        self.description = description
        self.average_cost = average_cost
        self.estimated_completion_time = estimated_completion_time


class SparePart:
    def __init__(self, id, title, description, compatibility_info, price, stock_availability):
        self.id = id
        self.title = title
        self.description = description
        self.compatibility_info = compatibility_info
        self.price = price
        self.stock_availability = stock_availability

class Feedback:
    def __init__(self, id, user_id, text, rating, timestamp):
        self.id = id
        self.user_id = user_id
        self.text = text
        self.rating = rating
        self.timestamp = timestamp


class FAQ:
    def __init__(self, id, question, answer):
        self.id = id
        self.question = question
        self.answer = answer

class Message_to_support:
    def __init__(self, id, message, user_id, status, sent):
        self.id = id
        self.message = message
        self.user_id = user_id
        self.status = status
        self.sent = sent


class Busy_slots:
    def __init__(self, id, date, busy_slots):
        self.id = id
        self.date  = date
        self.busy_slots = busy_slots