"""Pure functions: RawData → FundamentalsIndicators. No I/O."""
from stock_analytics.briefing.schema import FundamentalsIndicators, RawData


def _safe_div(num: float | None, den: float | None) -> float | None:
    if num is None or den is None or den == 0:
        return None
    return num / den


def compute_fundamentals_indicators(raw: RawData) -> FundamentalsIndicators:
    f = raw.fundamentals

    revenue_growth_yoy = None
    if f.revenue_ttm is not None and f.revenue_prior_ttm:
        revenue_growth_yoy = (f.revenue_ttm - f.revenue_prior_ttm) / f.revenue_prior_ttm

    revenue_cagr_3y = None
    if f.revenue_ttm and f.revenue_3y_ago and f.revenue_3y_ago > 0:
        revenue_cagr_3y = (f.revenue_ttm / f.revenue_3y_ago) ** (1 / 3) - 1

    net_debt = None
    if f.total_debt is not None and f.cash_and_equivalents is not None:
        net_debt = f.total_debt - f.cash_and_equivalents

    return FundamentalsIndicators(
        revenue_growth_yoy=revenue_growth_yoy,
        revenue_cagr_3y=revenue_cagr_3y,
        gross_margin=_safe_div(f.gross_profit_ttm, f.revenue_ttm),
        operating_margin=_safe_div(f.operating_income_ttm, f.revenue_ttm),
        net_margin=_safe_div(f.net_income_ttm, f.revenue_ttm),
        fcf_margin=_safe_div(f.free_cash_flow_ttm, f.revenue_ttm),
        fcf_to_net_income=_safe_div(f.free_cash_flow_ttm, f.net_income_ttm),
        roe=_safe_div(f.net_income_ttm, f.book_value),
        net_debt_to_ebitda=_safe_div(net_debt, f.ebitda_ttm),
        earnings_beat_streak=f.earnings_beat_streak,
    )
