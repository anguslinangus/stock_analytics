"""Programmatic red flag detection. Run on every briefing."""
from stock_analytics.briefing.schema import Indicators, RawData, RedFlag


def detect_red_flags(raw: RawData, indicators: Indicators) -> list[RedFlag]:
    flags: list[RedFlag] = []

    # Valuation red flags
    if indicators.valuation.ps is not None and indicators.valuation.ps > 25:
        flags.append(RedFlag(
            severity="warn",
            code="ps_extreme",
            message=f"P/S ratio {indicators.valuation.ps:.1f} is extreme; historically associated with subsequent multiple compression.",
        ))

    if indicators.valuation.pe_ttm is not None and indicators.valuation.pe_ttm < 0:
        flags.append(RedFlag(
            severity="warn",
            code="unprofitable",
            message="Company is unprofitable on TTM basis (negative P/E).",
        ))

    # Fundamentals red flags
    if indicators.fundamentals.fcf_margin is not None and indicators.fundamentals.fcf_margin < 0:
        flags.append(RedFlag(
            severity="warn",
            code="negative_fcf",
            message="Free cash flow margin is negative — company is burning cash.",
        ))

    if indicators.fundamentals.net_debt_to_ebitda is not None and indicators.fundamentals.net_debt_to_ebitda > 4:
        flags.append(RedFlag(
            severity="warn",
            code="high_leverage",
            message=f"Net debt / EBITDA at {indicators.fundamentals.net_debt_to_ebitda:.1f} indicates high leverage.",
        ))

    if indicators.fundamentals.revenue_growth_yoy is not None and indicators.fundamentals.revenue_growth_yoy < -0.10:
        flags.append(RedFlag(
            severity="critical",
            code="revenue_collapse",
            message=f"Revenue down {indicators.fundamentals.revenue_growth_yoy * 100:.1f}% YoY.",
        ))

    # Ownership red flags
    if raw.ownership.insider_net_buying_90d is not None and raw.ownership.insider_net_buying_90d < -1e8:
        flags.append(RedFlag(
            severity="warn",
            code="insider_selling_large",
            message=f"Insiders sold ${abs(raw.ownership.insider_net_buying_90d) / 1e6:.0f}M (net) in last 90 days.",
        ))

    return flags
