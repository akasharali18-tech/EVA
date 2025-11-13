import datetime

def get_time():
    """
    Get current time in 12-hour format
    
    Returns:
        str: Current time (e.g., "02:30 PM")
    """
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    return time_str

def get_date():
    """
    Get current date in readable format
    
    Returns:
        str: Current date (e.g., "Monday, January 15, 2024")
    """
    now = datetime.datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    return date_str

def get_day():
    """
    Get current day of the week
    
    Returns:
        str: Day name (e.g., "Monday")
    """
    now = datetime.datetime.now()
    return now.strftime("%A")