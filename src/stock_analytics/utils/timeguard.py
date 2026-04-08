"""Timezone discipline. All datetimes in the system are US/Eastern, timezone-aware."""
from datetime import datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")


def now_et() -> datetime:
    """Current time in US/Eastern. Use this once at the top of a run; thread `as_of` after."""
    return datetime.now(ET)


def ensure_et(dt: datetime) -> datetime:
    """Convert any datetime to US/Eastern. Naive datetimes are assumed to be ET."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ET)
    return dt.astimezone(ET)


def format_as_of(dt: datetime) -> str:
    """Render a datetime as the canonical 'YYYY-MM-DD HH:MM ET' header string."""
    et = ensure_et(dt)
    return et.strftime("%Y-%m-%d %H:%M ET")
