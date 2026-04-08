"""Valuation indicators including a simple, transparent DCF."""
from stock_analytics.briefing.schema import RawData, ValuationIndicators

# Hard-coded DCF defaults per spec §13. Displayed in briefing for critique.
DCF_WACC = 0.09
DCF_TERMINAL_GROWTH = 0.03
DCF_GROWTH_PATH = [0.25, 0.20, 0.16, 0.12, 0.08]  # 5-year fade


def _safe_div(num, den):
    if num is None or den is None or den == 0:
        return None
    return num / den


def _compute_dcf(raw: RawData) -> tuple[float | None, float | None]:
    """Returns (fair_value_per_share, upside_pct). None if inputs missing."""
    f = raw.fundamentals
    if f.free_cash_flow_ttm is None or f.shares_outstanding is None or f.shares_outstanding == 0:
        return None, None

    fcf = f.free_cash_flow_ttm
    pv_sum = 0.0
    for year, growth in enumerate(DCF_GROWTH_PATH, start=1):
        fcf = fcf * (1 + growth)
        pv_sum += fcf / ((1 + DCF_WACC) ** year)

    # Terminal value at end of forecast horizon
    terminal_fcf = fcf * (1 + DCF_TERMINAL_GROWTH)
    terminal_value = terminal_fcf / (DCF_WACC - DCF_TERMINAL_GROWTH)
    pv_terminal = terminal_value / ((1 + DCF_WACC) ** len(DCF_GROWTH_PATH))

    enterprise_value = pv_sum + pv_terminal
    # Adjust to equity value
    net_debt = (f.total_debt or 0) - (f.cash_and_equivalents or 0)
    equity_value = enterprise_value - net_debt

    fair_value_per_share = equity_value / f.shares_outstanding
    current = raw.snapshot.current_price
    upside_pct = (fair_value_per_share - current) / current if current else None

    return fair_value_per_share, upside_pct


def compute_valuation_indicators(raw: RawData) -> ValuationIndicators:
    s = raw.snapshot
    f = raw.fundamentals

    pe_ttm = _safe_div(s.market_cap, f.net_income_ttm)
    ps = _safe_div(s.market_cap, f.revenue_ttm)
    pb = _safe_div(s.market_cap, f.book_value)

    ev_ebitda = None
    if s.market_cap is not None and f.ebitda_ttm:
        ev = s.market_cap + (f.total_debt or 0) - (f.cash_and_equivalents or 0)
        ev_ebitda = ev / f.ebitda_ttm

    dcf_fv, dcf_up = _compute_dcf(raw)

    return ValuationIndicators(
        pe_ttm=pe_ttm,
        pe_forward=None,  # Requires forward earnings; v1 leaves None
        peg=None,         # Requires forward growth; v1 leaves None
        ev_ebitda=ev_ebitda,
        ps=ps,
        pb=pb,
        dcf_fair_value=dcf_fv,
        dcf_upside_pct=dcf_up,
        dcf_assumptions={
            "wacc": DCF_WACC,
            "terminal_growth": DCF_TERMINAL_GROWTH,
            "growth_path": DCF_GROWTH_PATH,
        },
    )
