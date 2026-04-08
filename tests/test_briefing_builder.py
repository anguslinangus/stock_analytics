import pytest

from stock_analytics.briefing.builder import build_briefing_markdown
from stock_analytics.briefing.schema import (
    CompositeScore, DimensionScore, FundamentalsIndicators, Indicators,
    ScoredBriefing, TechnicalsIndicators, ValuationIndicators,
)
from stock_analytics.scoring.red_flags import detect_red_flags


def _make_scored(raw):
    indicators = Indicators(
        fundamentals=FundamentalsIndicators(
            revenue_growth_yoy=0.667, fcf_margin=0.475, roe=1.0,
            net_debt_to_ebitda=-0.31, earnings_beat_streak=4,
        ),
        valuation=ValuationIndicators(
            pe_ttm=60.0, ps=30.0, ev_ebitda=45.85, pb=60.0,
            dcf_fair_value=850.0, dcf_upside_pct=-0.056,
            dcf_assumptions={"wacc": 0.09, "terminal_growth": 0.03, "growth_path": [0.25, 0.20, 0.16, 0.12, 0.08]},
        ),
        technicals=TechnicalsIndicators(
            sma_50=880.0, sma_200=750.0, price_vs_sma200_pct=0.20,
            golden_cross=True, rsi_14=58, macd_signal="positive",
        ),
    )
    scores = CompositeScore(
        fundamentals=DimensionScore(value=8.5, hits=["revenue_growth_high(+2)"]),
        valuation=DimensionScore(value=4.5, hits=["ps_extreme(-1.5)"]),
        technicals=DimensionScore(value=7.5, hits=["above_sma200(+1.5)"]),
        sentiment=DimensionScore(value=6.0, hits=["analyst_consensus_buy(+1)"]),
        composite=6.6,
    )
    return ScoredBriefing(
        raw=raw, indicators=indicators, scores=scores,
        red_flags=detect_red_flags(raw, indicators), as_of=raw.as_of,
    )


def test_briefing_contains_timeguard(sample_nvda_raw):
    md = build_briefing_markdown(_make_scored(sample_nvda_raw))
    assert "TIMEGUARD" in md
    assert "2026-04-09" in md


def test_briefing_has_all_sections(sample_nvda_raw):
    md = build_briefing_markdown(_make_scored(sample_nvda_raw))
    for header in [
        "## 0 · Snapshot",
        "## 1 · Fundamentals",
        "## 2 · Valuation",
        "## 3 · Technicals",
        "## 4 · Sentiment & Flow",
        "## 5 · Aggregate",
        "## 6 · Red Flags",
        "## 7 · Data Provenance",
    ]:
        assert header in md, f"Missing section: {header}"


def test_briefing_includes_scores(sample_nvda_raw):
    md = build_briefing_markdown(_make_scored(sample_nvda_raw))
    assert "8.5" in md  # fundamentals score
    assert "Composite" in md
    assert "6.6" in md


def test_briefing_includes_rubric_hits(sample_nvda_raw):
    md = build_briefing_markdown(_make_scored(sample_nvda_raw))
    assert "revenue_growth_high(+2)" in md
    assert "ps_extreme(-1.5)" in md


def test_briefing_includes_dcf_assumptions(sample_nvda_raw):
    md = build_briefing_markdown(_make_scored(sample_nvda_raw))
    assert "WACC" in md or "wacc" in md
    assert "0.09" in md or "9" in md
