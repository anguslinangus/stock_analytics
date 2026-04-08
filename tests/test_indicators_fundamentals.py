import pytest

from stock_analytics.indicators.fundamentals import compute_fundamentals_indicators


def test_revenue_growth_yoy(sample_nvda_raw):
    ind = compute_fundamentals_indicators(sample_nvda_raw)
    # 100B vs 60B prior = 66.67%
    assert ind.revenue_growth_yoy == pytest.approx(0.6667, rel=1e-3)


def test_revenue_cagr_3y(sample_nvda_raw):
    ind = compute_fundamentals_indicators(sample_nvda_raw)
    # (100/27)^(1/3) - 1 ≈ 0.547
    assert ind.revenue_cagr_3y == pytest.approx(0.5475, rel=1e-3)


def test_margins(sample_nvda_raw):
    ind = compute_fundamentals_indicators(sample_nvda_raw)
    assert ind.gross_margin == pytest.approx(0.75)
    assert ind.operating_margin == pytest.approx(0.60)
    assert ind.net_margin == pytest.approx(0.50)
    assert ind.fcf_margin == pytest.approx(0.475)


def test_fcf_to_net_income(sample_nvda_raw):
    ind = compute_fundamentals_indicators(sample_nvda_raw)
    assert ind.fcf_to_net_income == pytest.approx(0.95)


def test_roe(sample_nvda_raw):
    ind = compute_fundamentals_indicators(sample_nvda_raw)
    # 50B / 50B = 1.0
    assert ind.roe == pytest.approx(1.0)


def test_net_debt_to_ebitda_negative_when_net_cash(sample_nvda_raw):
    ind = compute_fundamentals_indicators(sample_nvda_raw)
    # debt 10B - cash 30B = -20B; / 65B EBITDA = -0.308
    assert ind.net_debt_to_ebitda == pytest.approx(-0.3077, rel=1e-3)


def test_handles_missing_fields_gracefully():
    from stock_analytics.briefing.schema import (
        AnalystData, CompanySnapshot, FundamentalsData, NewsData,
        OwnershipData, PriceData, RawData,
    )
    from datetime import datetime
    from zoneinfo import ZoneInfo
    et = ZoneInfo("America/New_York")
    raw = RawData(
        snapshot=CompanySnapshot(ticker="X", name="X", current_price=10.0),
        price=PriceData(history=[], source="t", fetched_at=datetime.now(et)),
        fundamentals=FundamentalsData(source="t", fetched_at=datetime.now(et)),
        ownership=OwnershipData(source="t", fetched_at=datetime.now(et)),
        analyst=AnalystData(source="t", fetched_at=datetime.now(et)),
        news=NewsData(items=[], source="t", fetched_at=datetime.now(et)),
        as_of=datetime.now(et),
    )
    ind = compute_fundamentals_indicators(raw)
    assert ind.revenue_growth_yoy is None
    assert ind.gross_margin is None
