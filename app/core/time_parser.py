from datetime import time
from typing import List, NamedTuple
import re
import logging

logger = logging.getLogger(__name__)


class HoursEntry(NamedTuple):
    day_of_week: int
    open_time: time
    close_time: time


def parse_time(time_str: str) -> time:
    """Convert time string (e.g., '11:00 am', '11 am', '11:30 pm') to time object"""
    time_str = time_str.strip().lower()

    # Handle various time formats
    match = re.match(r"(\d+)(?::(\d+))?\s*(am|pm)", time_str)
    if not match:
        raise ValueError(f"Invalid time format: {time_str}")

    hour, minute, meridiem = match.groups()
    hour = int(hour)
    minute = int(minute) if minute else 0

    if meridiem == "pm" and hour != 12:
        hour += 12
    elif meridiem == "am" and hour == 12:
        hour = 0

    return time(hour, minute)


def parse_day_range(day_range: str) -> List[int]:
    """Parse a day range like 'Mon-Thu' or 'Mon' into list of day indices"""
    day_range = day_range.strip().lower()
    days = {
        "sun": 0,
        "sunday": 0,
        "mon": 1,
        "monday": 1,
        "tue": 2,
        "tues": 2,
        "tuesday": 2,
        "wed": 3,
        "wednesday": 3,
        "thu": 4,
        "thur": 4,
        "thurs": 4,
        "thursday": 4,
        "fri": 5,
        "friday": 5,
        "sat": 6,
        "saturday": 6,
    }

    try:
        if "-" in day_range:
            start, end = map(str.strip, day_range.split("-"))
            start_idx = days[start]
            end_idx = days[end]
            if end_idx < start_idx:  # Handle wrap around (e.g., Sat-Sun)
                return list(range(start_idx, 7)) + list(range(0, end_idx + 1))
            return list(range(start_idx, end_idx + 1))
        return [days[day_range]]
    except KeyError as e:
        logger.error(f"Invalid day in range '{day_range}': {str(e)}")
        raise ValueError(f"Invalid day in range '{day_range}'")


def parse_hours_string(hours_str: str) -> List[HoursEntry]:
    """Parse complex hours string into list of HoursEntry objects"""
    entries = []
    # Split different day ranges (separated by /)
    schedules = [s.strip() for s in hours_str.split("/")]

    for schedule in schedules:
        # Split days from times
        try:
            # Handle cases where there might be extra spaces
            parts = [p for p in schedule.split(" ") if p]
            # Find the index where times start (first part containing numbers)
            time_start_idx = next(
                i for i, part in enumerate(parts) if any(c.isdigit() for c in part)
            )

            days_part = " ".join(parts[:time_start_idx])
            times = " ".join(parts[time_start_idx:])

            # Handle multiple day ranges (e.g., "Mon-Thu, Sun")
            day_ranges = [r.strip() for r in days_part.split(",")]

            # Parse the time range
            times = times.strip()
            if "-" not in times:
                raise ValueError(f"Invalid time range format: {times}")

            open_time_str, close_time_str = map(str.strip, times.split("-"))
            open_time = parse_time(open_time_str)
            close_time = parse_time(close_time_str)

            # Create entries for each day in each range
            for day_range in day_ranges:
                for day in parse_day_range(day_range):
                    entries.append(HoursEntry(day, open_time, close_time))

        except Exception as e:
            logger.error(f"Error parsing schedule '{schedule}': {str(e)}")
            raise ValueError(f"Error parsing schedule '{schedule}': {str(e)}")

    return entries
