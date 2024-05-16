from datetime import datetime, timedelta

def divide_into_hourly_intervals(selected_date):
    # Parse the selected date
    date_obj = datetime.strptime(selected_date, "%d.%m.%Y")

    # Initialize list to store hourly intervals
    hourly_intervals = []

    # Start from 09:00 and go until 18:00 with one hour interval
    current_time = datetime(date_obj.year, date_obj.month, date_obj.day, 9, 0)  # Start from 09:00
    end_time = datetime(date_obj.year, date_obj.month, date_obj.day, 18, 0)  # End at 18:00

    while current_time < end_time:
        # Check if the current time is not within existing orders
        if not is_time_within_existing_orders(current_time):
            hourly_intervals.append(current_time.strftime("%H:%M"))
        
        # Move to the next hour
        current_time += timedelta(hours=2)

    return hourly_intervals

def is_time_within_existing_orders(current_time):
    # Placeholder function to check if the current time falls within existing orders
    # You need to implement this function based on your database structure
    return False  # Assuming no existing orders for demonstration


