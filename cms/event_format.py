from datetime import date, time


def format_event_date(value: date | None) -> str:
    if not value:
        return ""
    return value.strftime(f"{value.day} %B %Y")


def format_event_time(start: time | None, end: time | None) -> str:
    if not start:
        return ""

    def fmt(t: time) -> str:
        hour = t.hour % 12 or 12
        minute = t.minute
        suffix = "AM" if t.hour < 12 else "PM"
        if minute:
            return f"{hour}:{minute:02d} {suffix}"
        return f"{hour} {suffix}"

    if end and end != start:
        return f"{fmt(start)} – {fmt(end)}"
    return fmt(start)
