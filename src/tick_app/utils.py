from datetime import datetime, timedelta

class ProjectNotFound(Exception):
    pass

class TimerNotRunning(Exception):
    pass

def format_duration(seconds: int) -> str:
    if seconds is None:
        return ""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

def parse_duration_string(s: str) -> int:
    total_seconds = 0
    # Regex to find numbers followed by h, m, or s
    import re
    matches = re.findall(r'(\d+)([hms])', s)
    for value, unit in matches:
        value = int(value)
        if unit == 'h':
            total_seconds += value * 3600
        elif unit == 'm':
            total_seconds += value * 60
        elif unit == 's':
            total_seconds += value
    return total_seconds

def get_current_datetime() -> datetime:
    return datetime.utcnow()

def parse_date_string(s: str) -> datetime:
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unable to parse date string: {s}. Expected format YYYY-MM-DD [HH:MM].")

def get_start_of_day(dt: datetime) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

def get_start_of_week(dt: datetime) -> datetime:
    start_of_day = get_start_of_day(dt)
    return start_of_day - timedelta(days=start_of_day.weekday())

def get_start_of_month(dt: datetime) -> datetime:
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
