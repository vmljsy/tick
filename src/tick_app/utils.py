from datetime import datetime, timedelta, UTC
import pytz

from .config import get_user_timezone

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
    return datetime.now(UTC)

def convert_utc_to_local(dt_utc: datetime) -> datetime:
    if dt_utc.tzinfo is None: # Assume naive datetime is UTC
        dt_utc = dt_utc.replace(tzinfo=UTC)
    local_tz = pytz.timezone(get_user_timezone())
    return dt_utc.astimezone(local_tz)

def convert_local_to_utc(dt_local: datetime) -> datetime:
    local_tz = pytz.timezone(get_user_timezone())
    if dt_local.tzinfo is None: # Assume naive datetime is local
        dt_local = local_tz.localize(dt_local)
    return dt_local.astimezone(UTC)

def parse_date_string(s: str, as_local: bool = True) -> datetime:
    # Try parsing with various formats
    dt_naive = None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt_naive = datetime.strptime(s, fmt)
            break
        except ValueError:
            continue
    
    if dt_naive is None:
        raise ValueError(f"Unable to parse date string: {s}. Expected format YYYY-MM-DD [HH:MM[:SS]].")

    if as_local:
        return convert_local_to_utc(dt_naive)
    return dt_naive.replace(tzinfo=UTC) # Return as UTC if not local

def get_start_of_day(dt: datetime) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

def get_start_of_week(dt: datetime) -> datetime:
    start_of_day = get_start_of_day(dt)
    return start_of_day - timedelta(days=start_of_day.weekday())

def get_start_of_month(dt: datetime) -> datetime:
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
