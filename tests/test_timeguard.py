from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from stock_analytics.utils.timeguard import now_et, ensure_et, format_as_of


def test_now_et_returns_timezone_aware():
    result = now_et()
    assert result.tzinfo is not None
    assert result.tzinfo == ZoneInfo("America/New_York")


def test_ensure_et_converts_naive_to_et():
    naive = datetime(2026, 4, 9, 12, 0, 0)
    result = ensure_et(naive)
    assert result.tzinfo == ZoneInfo("America/New_York")


def test_ensure_et_converts_utc_to_et():
    utc = datetime(2026, 4, 9, 16, 0, 0, tzinfo=timezone.utc)
    result = ensure_et(utc)
    assert result.tzinfo == ZoneInfo("America/New_York")
    assert result.hour == 12  # EDT offset in April


def test_format_as_of_renders_human_readable():
    dt = datetime(2026, 4, 9, 16, 0, 0, tzinfo=ZoneInfo("America/New_York"))
    assert format_as_of(dt) == "2026-04-09 16:00 ET"
