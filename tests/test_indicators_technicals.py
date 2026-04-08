from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from stock_analytics.briefing.schema import (
    AnalystData, CompanySnapshot, FundamentalsData, NewsData,
    OwnershipData, PriceData, PricePoint, RawData,
)
from stock_analytics.indicators.technicals import compute_technicals_indicators

ET = ZoneInfo("America/New_York")


def _make_raw_with_prices(closes: list[float]) -> RawData:
    base = datetime(2025, 1, 1, tzinfo=ET)
    history = [
        PricePoint(
            date=base + timedelta(days=i),
            open=c, high=c * 1.01, low=c * 0.99, close=c, volume=1_000_000,
        )
        for i, c in enumerate(closes)
    ]
    now = datetime(2026, 4, 9, tzinfo=ET)
    return RawData(
        snapshot=CompanySnapshot(
            ticker="T", name="T", current_price=closes[-1],
            week52_high=max(closes), week52_low=min(closes),
        ),
        price=PriceData(history=history, source="t", fetched_at=now),
        fundamentals=FundamentalsData(source="t", fetched_at=now),
        ownership=OwnershipData(source="t", fetched_at=now),
        analyst=AnalystData(source="t", fetched_at=now),
        news=NewsData(items=[], source="t", fetched_at=now),
        as_of=now,
    )


def test_sma_calculation():
    closes = list(range(1, 251))  # 1..250
    raw = _make_raw_with_prices([float(c) for c in closes])
    ind = compute_technicals_indicators(raw)
    # SMA50 = mean of last 50 (201..250) = 225.5
    assert ind.sma_50 == pytest.approx(225.5)
    # SMA200 = mean of last 200 (51..250) = 150.5
    assert ind.sma_200 == pytest.approx(150.5)


def test_price_above_smas():
    closes = [100.0] * 250
    raw = _make_raw_with_prices(closes)
    ind = compute_technicals_indicators(raw)
    assert ind.price_vs_sma50_pct == pytest.approx(0.0)


def test_golden_cross_when_short_above_long():
    closes = list(range(1, 251))
    raw = _make_raw_with_prices([float(c) for c in closes])
    ind = compute_technicals_indicators(raw)
    assert ind.golden_cross is True
    assert ind.death_cross is False


def test_rsi_in_valid_range():
    import math
    closes = [100 + 5 * math.sin(i / 5) for i in range(250)]
    raw = _make_raw_with_prices(closes)
    ind = compute_technicals_indicators(raw)
    assert 0 <= ind.rsi_14 <= 100


def test_distance_from_52w_high():
    closes = [float(c) for c in list(range(1, 250)) + [200]]
    raw = _make_raw_with_prices(closes)
    ind = compute_technicals_indicators(raw)
    # current 200, high 249, distance = (200-249)/249
    assert ind.distance_from_52w_high_pct == pytest.approx(-0.1968, rel=1e-3)


def test_returns_none_for_short_history():
    closes = [100.0] * 10
    raw = _make_raw_with_prices(closes)
    ind = compute_technicals_indicators(raw)
    assert ind.sma_200 is None
    assert ind.sma_50 is None
