"""Deterministic scoring rubric. Each dimension → 0–10 with explicit hit list."""
from stock_analytics.briefing.schema import (
    AnalystData, CompositeScore, DimensionScore, FundamentalsIndicators,
    Indicators, OwnershipData, TechnicalsIndicators, ValuationIndicators,
)


def _clamp(x: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return max(lo, min(hi, x))


def score_fundamentals(ind: FundamentalsIndicators) -> DimensionScore:
    score = 5.0
    hits: list[str] = []

    g = ind.revenue_growth_yoy
    if g is not None:
        if g >= 0.30:
            score += 2.0; hits.append("revenue_growth_high(+2)")
        elif g >= 0.10:
            score += 1.0; hits.append("revenue_growth_moderate(+1)")
        elif g < 0:
            score -= 2.0; hits.append("revenue_declining(-2)")

    fm = ind.fcf_margin
    if fm is not None:
        if fm >= 0.20:
            score += 1.5; hits.append("fcf_strong(+1.5)")
        elif fm < 0:
            score -= 1.5; hits.append("fcf_negative(-1.5)")

    if ind.roe is not None:
        if ind.roe >= 0.20:
            score += 1.0; hits.append("roe_strong(+1)")
        elif ind.roe < 0.05:
            score -= 1.0; hits.append("roe_weak(-1)")

    nd = ind.net_debt_to_ebitda
    if nd is not None:
        if nd < 0:
            score += 0.5; hits.append("net_cash_position(+0.5)")
        elif nd > 3:
            score -= 1.0; hits.append("high_leverage(-1)")

    if ind.earnings_beat_streak >= 4:
        score += 0.5; hits.append("beat_streak(+0.5)")

    return DimensionScore(value=_clamp(score), hits=hits)


def score_valuation(ind: ValuationIndicators) -> DimensionScore:
    score = 5.0
    hits: list[str] = []

    pe = ind.pe_ttm
    if pe is not None:
        if pe < 0:
            score -= 1.0; hits.append("pe_negative(-1)")
        elif pe > 50:
            score -= 2.0; hits.append("pe_very_premium(-2)")
        elif pe > 30:
            score -= 1.0; hits.append("pe_premium(-1)")
        elif pe < 15:
            score += 1.0; hits.append("pe_cheap(+1)")

    ps = ind.ps
    if ps is not None:
        if ps > 20:
            score -= 1.5; hits.append("ps_extreme(-1.5)")
        elif ps < 3:
            score += 0.5; hits.append("ps_reasonable(+0.5)")

    up = ind.dcf_upside_pct
    if up is not None:
        if up >= 0.30:
            score += 2.5; hits.append("dcf_significant_upside(+2.5)")
        elif up >= 0.10:
            score += 1.0; hits.append("dcf_moderate_upside(+1)")
        elif up <= -0.20:
            score -= 1.5; hits.append("dcf_overvalued(-1.5)")

    return DimensionScore(value=_clamp(score), hits=hits)


def score_technicals(ind: TechnicalsIndicators) -> DimensionScore:
    score = 5.0
    hits: list[str] = []

    if ind.price_vs_sma200_pct is not None:
        if ind.price_vs_sma200_pct > 0:
            score += 1.5; hits.append("above_sma200(+1.5)")
        else:
            score -= 1.5; hits.append("below_sma200(-1.5)")

    if ind.golden_cross:
        score += 1.0; hits.append("golden_cross(+1)")
    if ind.death_cross:
        score -= 1.0; hits.append("death_cross(-1)")

    rsi = ind.rsi_14
    if rsi is not None:
        if 40 <= rsi <= 65:
            score += 1.0; hits.append("rsi_healthy(+1)")
        elif rsi > 75:
            score -= 1.0; hits.append("rsi_overbought(-1)")
        elif rsi < 30:
            score -= 0.5; hits.append("rsi_oversold(-0.5)")

    if ind.macd_signal == "positive":
        score += 0.5; hits.append("macd_positive(+0.5)")
    elif ind.macd_signal == "negative":
        score -= 0.5; hits.append("macd_negative(-0.5)")

    if ind.volume_20d_vs_60d_pct is not None and ind.volume_20d_vs_60d_pct > 0.05:
        score += 0.5; hits.append("volume_confirming(+0.5)")

    return DimensionScore(value=_clamp(score), hits=hits)


def score_sentiment(analyst: AnalystData, ownership: OwnershipData) -> DimensionScore:
    score = 5.0
    hits: list[str] = []

    total = analyst.num_buy + analyst.num_hold + analyst.num_sell
    if total > 0:
        buy_ratio = analyst.num_buy / total
        if buy_ratio >= 0.75:
            score += 2.0; hits.append("analyst_consensus_strong_buy(+2)")
        elif buy_ratio >= 0.50:
            score += 1.0; hits.append("analyst_consensus_buy(+1)")
        elif buy_ratio < 0.25:
            score -= 1.5; hits.append("analyst_consensus_bearish(-1.5)")

    if ownership.institutional_pct_change_qoq is not None:
        if ownership.institutional_pct_change_qoq > 0.01:
            score += 1.0; hits.append("institutional_buying(+1)")
        elif ownership.institutional_pct_change_qoq < -0.01:
            score -= 1.0; hits.append("institutional_selling(-1)")

    if ownership.insider_net_buying_90d is not None:
        if ownership.insider_net_buying_90d > 0:
            score += 1.5; hits.append("insider_buying(+1.5)")
        elif ownership.insider_net_buying_90d < -1e8:  # >$100M selling
            score -= 1.5; hits.append("insider_selling_large(-1.5)")

    return DimensionScore(value=_clamp(score), hits=hits)


def compose(
    indicators: Indicators,
    analyst: AnalystData,
    ownership: OwnershipData,
) -> CompositeScore:
    f = score_fundamentals(indicators.fundamentals)
    v = score_valuation(indicators.valuation)
    t = score_technicals(indicators.technicals)
    s = score_sentiment(analyst, ownership)

    weights = {
        "fundamentals": 0.30,
        "valuation": 0.30,
        "technicals": 0.20,
        "sentiment": 0.20,
    }
    composite = (
        f.value * weights["fundamentals"]
        + v.value * weights["valuation"]
        + t.value * weights["technicals"]
        + s.value * weights["sentiment"]
    )
    return CompositeScore(
        fundamentals=f, valuation=v, technicals=t, sentiment=s,
        weights=weights, composite=round(composite, 2),
    )
