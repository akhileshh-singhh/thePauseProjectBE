"""Parse legacy JSON date/time strings into structured fields."""

import re
from datetime import date, datetime, time

_MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def parse_event_date(text: str) -> date:
    text = text.strip()
    try:
        return datetime.strptime(text, "%d %B %Y").date()
    except ValueError:
        pass
    try:
        return datetime.strptime(text, "%d %b %Y").date()
    except ValueError:
        pass
  # fallback: today
    return date.today()


def _parse_clock(token: str) -> time | None:
    token = token.strip().lower().replace(".", "")
    match = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$", token)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    meridiem = match.group(3)
    if meridiem == "pm" and hour < 12:
        hour += 12
    if meridiem == "am" and hour == 12:
        hour = 0
    return time(hour, minute)


def parse_event_times(text: str) -> tuple[time, time | None]:
    text = text.strip().replace("–", "-").replace("—", "-")
    if "-" in text:
        start_raw, end_raw = [part.strip() for part in text.split("-", 1)]
        start = _parse_clock(start_raw) or time(10, 0)
        end = _parse_clock(end_raw)
        return start, end
    start = _parse_clock(text) or time(10, 0)
    return start, None
