"""On-disk JSON cache keyed by ticker + ET date. One file per (ticker, day)."""
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from stock_analytics.utils.timeguard import ensure_et


def cache_path(ticker: str, as_of: datetime, root: Path) -> Path:
    et = ensure_et(as_of)
    return root / f"{ticker.upper()}_{et.strftime('%Y-%m-%d')}.json"


def read_cache(ticker: str, as_of: datetime, root: Path) -> dict[str, Any] | None:
    path = cache_path(ticker, as_of, root)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def write_cache(ticker: str, as_of: datetime, payload: dict[str, Any], root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = cache_path(ticker, as_of, root)
    path.write_text(json.dumps(payload, indent=2, default=str))
    return path
