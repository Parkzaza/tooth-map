import calendar
from datetime import datetime

def generate_calendar(year=None, month=None):
    if not year or not month:
        now = datetime.now()
        year = now.year
        month = now.month
    
    cal = calendar.HTMLCalendar(calendar.SUNDAY)
    return cal.formatmonth(year, month)
