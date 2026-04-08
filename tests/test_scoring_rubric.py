import pytest

from stock_analytics.briefing.schema import (
    FundamentalsIndicators, Indicators, TechnicalsIndicators, ValuationIndicators,
)
from stock_analytics.scoring.rubric import (
    score_fundamentals, score_valuation, score_technicals, score_sentiment, compose,
)


def test_score_fundamentals_high_growth_high_margin():
    ind = FundamentalsIndicators(
        revenue_growth_yoy=0.50, fcf_margin=0.30, roe=0.40,
        net_debt_to_ebitda=-0.5, earnings_beat_streak=4,
    )
    result = score_fundamentals(ind)
    assert result.value >= 8.0
    assert any("revenue_growth_high" in h for h in result.hits)


def test_score_fundamentals_revenue_declining():
    ind = FundamentalsIndicators(
        revenue_growth_yoy=-0.10, fcf_margin=0.05, roe=0.05,
        net_debt_to_ebitda=3.0,
    )
    result = score_fundamentals(ind)
    assert result.value <= 4.0
    assert any("revenue_declining" in h for h in result.hits)


def test_score_valuation_premium_pe_penalised():
    ind = ValuationIndicators(pe_ttm=80, ps=30, dcf_upside_pct=-0.30)
    result = score_valuation(ind)
    assert result.value <= 4.0


def test_score_valuation_undervalued_dcf():
    ind = ValuationIndicators(pe_ttm=15, ps=2, dcf_upside_pct=0.40)
    result = score_valuation(ind)
    assert result.value >= 7.0


def test_score_technicals_uptrend():
    ind = TechnicalsIndicators(
        price_vs_sma200_pct=0.15, golden_cross=True, rsi_14=58,
        macd_signal="positive", volume_20d_vs_60d_pct=0.10,
    )
    result = score_technicals(ind)
    assert result.value >= 7.0


def test_score_sentiment_strong_buy_consensus():
    from stock_analytics.briefing.schema import AnalystData, OwnershipData
    from datetime import datetime
    from zoneinfo import ZoneInfo
    et = ZoneInfo("America/New_York")
    analyst = AnalystData(
        consensus="BUY", num_buy=30, num_hold=3, num_sell=0,
        source="t", fetched_at=datetime.now(et),
    )
    ownership = OwnershipData(
        institutional_pct_change_qoq=0.02, insider_net_buying_90d=0,
        source="t", fetched_at=datetime.now(et),
    )
    result = score_sentiment(analyst, ownership)
    assert result.value >= 6.5


def test_compose_weighted_average():
    indicators = Indicators(
        fundamentals=FundamentalsIndicators(
            revenue_growth_yoy=0.50, fcf_margin=0.30, roe=0.40,
            net_debt_to_ebitda=-0.5, earnings_beat_streak=4,
        ),
        valuation=ValuationIndicators(pe_ttm=80, ps=30, dcf_upside_pct=-0.30),
        technicals=TechnicalsIndicators(
            price_vs_sma200_pct=0.15, golden_cross=True, rsi_14=58,
            macd_signal="positive", volume_20d_vs_60d_pct=0.10,
        ),
    )
    from stock_analytics.briefing.schema import AnalystData, OwnershipData
    from datetime import datetime
    from zoneinfo import ZoneInfo
    et = ZoneInfo("America/New_York")
    analyst = AnalystData(
        consensus="BUY", num_buy=30, num_hold=3, num_sell=0,
        source="t", fetched_at=datetime.now(et),
    )
    ownership = OwnershipData(
        institutional_pct_change_qoq=0.02, insider_net_buying_90d=0,
        source="t", fetched_at=datetime.now(et),
    )
    composite = compose(indicators, analyst, ownership)
    assert 0 <= composite.composite <= 10
    assert composite.weights["fundamentals"] == 0.30
