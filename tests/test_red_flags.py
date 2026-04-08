import pytest

from stock_analytics.briefing.schema import (
    FundamentalsIndicators, Indicators, TechnicalsIndicators, ValuationIndicators,
)
from stock_analytics.scoring.red_flags import detect_red_flags


def test_detects_extreme_ps(sample_nvda_raw):
    indicators = Indicators(
        fundamentals=FundamentalsIndicators(),
        valuation=ValuationIndicators(ps=35.0),
        technicals=TechnicalsIndicators(),
    )
    flags = detect_red_flags(sample_nvda_raw, indicators)
    assert any(f.code == "ps_extreme" for f in flags)


def test_detects_negative_fcf(sample_nvda_raw):
    indicators = Indicators(
        fundamentals=FundamentalsIndicators(fcf_margin=-0.05),
        valuation=ValuationIndicators(),
        technicals=TechnicalsIndicators(),
    )
    flags = detect_red_flags(sample_nvda_raw, indicators)
    assert any(f.code == "negative_fcf" for f in flags)


def test_detects_insider_selling_acceleration(sample_nvda_raw):
    indicators = Indicators(
        fundamentals=FundamentalsIndicators(),
        valuation=ValuationIndicators(),
        technicals=TechnicalsIndicators(),
    )
    flags = detect_red_flags(sample_nvda_raw, indicators)
    # Sample NVDA fixture has -250M insider net buying
    assert any(f.code == "insider_selling_large" for f in flags)


def test_no_flags_for_healthy_company():
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from stock_analytics.briefing.schema import (
        AnalystData, CompanySnapshot, FundamentalsData, NewsData,
        OwnershipData, PriceData, RawData,
    )
    et = ZoneInfo("America/New_York")
    now = datetime.now(et)
    raw = RawData(
        snapshot=CompanySnapshot(ticker="X", name="X", current_price=100.0),
        price=PriceData(history=[], source="t", fetched_at=now),
        fundamentals=FundamentalsData(source="t", fetched_at=now),
        ownership=OwnershipData(
            insider_net_buying_90d=10_000_000, source="t", fetched_at=now,
        ),
        analyst=AnalystData(source="t", fetched_at=now),
        news=NewsData(items=[], source="t", fetched_at=now),
        as_of=now,
    )
    indicators = Indicators(
        fundamentals=FundamentalsIndicators(fcf_margin=0.20),
        valuation=ValuationIndicators(ps=5.0),
        technicals=TechnicalsIndicators(),
    )
    flags = detect_red_flags(raw, indicators)
    assert all(f.severity != "critical" for f in flags)
