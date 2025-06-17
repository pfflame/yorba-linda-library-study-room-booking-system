import datetime

def day_to_weekday_index(day_name: str) -> int:
    """
    Convert a day name like 'Monday'/'Tuesday'... into an integer:
      Monday=0, Tuesday=1, ..., Sunday=6
    """
    day_map = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }
    # Make it case-insensitive
    day_name_lower = day_name.strip().lower()
    if day_name_lower not in day_map:
        raise ValueError(f"Invalid day of week: {day_name}")
    return day_map[day_name_lower]

def get_next_day_of_week(day_name: str) -> datetime.date:
    """
    Return the date object for the *upcoming* `day_name`.
    If 'day_name' is today, return today.
    E.g. get_next_day_of_week("Saturday").
    """
    today = datetime.date.today()
    target_idx = day_to_weekday_index(day_name)
    offset = (target_idx - today.weekday()) % 7
    return today + datetime.timedelta(days=offset)

def format_dow_label(dt: datetime.date) -> str:
    """
    Return a string like 'Saturday, January 11, 2025'
    using the date's actual day name, e.g. dt.strftime("%A, %B %d, %Y").
    """
    # The day part needs to be handled carefully to avoid leading zeros for single-digit days
    # when not using platform-specific '#' or '-' format codes (which are not universally supported).
    day_str = str(dt.day)
    return dt.strftime(f"%A, %B {day_str}, %Y")