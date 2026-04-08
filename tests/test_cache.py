import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from stock_analytics.utils.cache import cache_path, read_cache, write_cache


def test_cache_path_format(tmp_path):
    p = cache_path("NVDA", datetime(2026, 4, 9, tzinfo=ZoneInfo("America/New_York")), root=tmp_path)
    assert p == tmp_path / "NVDA_2026-04-09.json"


def test_write_then_read_roundtrip(tmp_path):
    payload = {"ticker": "NVDA", "value": 42}
    as_of = datetime(2026, 4, 9, tzinfo=ZoneInfo("America/New_York"))
    write_cache("NVDA", as_of, payload, root=tmp_path)
    result = read_cache("NVDA", as_of, root=tmp_path)
    assert result == payload


def test_read_cache_missing_returns_none(tmp_path):
    as_of = datetime(2026, 4, 9, tzinfo=ZoneInfo("America/New_York"))
    assert read_cache("NVDA", as_of, root=tmp_path) is None


def test_write_cache_creates_root_if_missing(tmp_path):
    nested = tmp_path / "data"
    as_of = datetime(2026, 4, 9, tzinfo=ZoneInfo("America/New_York"))
    write_cache("NVDA", as_of, {"x": 1}, root=nested)
    assert (nested / "NVDA_2026-04-09.json").exists()
