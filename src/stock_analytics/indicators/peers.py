"""Peer/industry median attachment.

v1: pass-through. The fetcher layer will pull industry medians from
yfinance when possible and inject them via this helper. Indicators stay
a pure function — peers are merged at compose time, not fetched here.
"""
from stock_analytics.briefing.schema import ValuationIndicators


def attach_peer_medians(
    valuation: ValuationIndicators,
    industry_pe_median: float | None,
    industry_ev_ebitda_median: float | None,
) -> ValuationIndicators:
    return valuation.model_copy(
        update={
            "industry_pe_median": industry_pe_median,
            "industry_ev_ebitda_median": industry_ev_ebitda_median,
        }
    )
