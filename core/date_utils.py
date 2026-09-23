from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
import re
PACIFIC = ZoneInfo("America/Los_Angeles")
DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
def library_now():
    return datetime.now(PACIFIC)
def day_to_weekday_index(day_name):
    try:
        return DAYS.index(day_name.strip().lower())
    except ValueError:
        raise ValueError("Use a full weekday name, such as Saturday") from None
def get_next_day_of_week(day_name, today=None):
    today = today or library_now().date()
    return today + timedelta(days=(day_to_weekday_index(day_name) - today.weekday()) % 7)
def parse_time(value):
    value = value.strip().lower().replace(" ", "")
    if not re.fullmatch(r"(?:[01]?\d|2[0-3]):00|(?:0?[1-9]|1[0-2]):00(?:am|pm)", value):
        raise ValueError("Times must start on the hour, e.g. 09:00 or 1:00pm")
    return datetime.strptime(value, "%I:%M%p" if value.endswith(("am", "pm")) else "%H:%M").strftime("%H:%M")
def validate_request(request, now=None):
    from config.settings import ROOM_CAPACITIES
    now = now or library_now()
    ahead = (request.target_date - now.date()).days
    if not 0 <= ahead <= 3:
        raise ValueError("The library allows reservations from today through 3 days ahead")
    if request.target_date.weekday() == 6:
        raise ValueError("The library is closed on Sundays")
    if request.room_name not in ROOM_CAPACITIES:
        raise ValueError("Unknown room; use --list-rooms for exact names")
    if not 1 <= request.party_size <= ROOM_CAPACITIES[request.room_name]:
        raise ValueError("Party size exceeds the selected room capacity or is below 1")
    slots = [parse_time(t) for t in request.time_slots]
    if len(slots) not in (1, 2) or len(set(slots)) != len(slots):
        raise ValueError("Request one or two distinct 1-hour slots (2 hours maximum per day)")
    close_hour = 17 if request.target_date.weekday() in (4, 5) else 20
    for slot in slots:
        hour = int(slot[:2])
        if not 9 <= hour < close_hour:
            raise ValueError("Requested hour is outside regular library hours")
        if datetime.combine(request.target_date, datetime.strptime(slot, "%H:%M").time(), PACIFIC) <= now:
            raise ValueError("Requested start time is in the past")
    request.time_slots = sorted(slots)
    return request
