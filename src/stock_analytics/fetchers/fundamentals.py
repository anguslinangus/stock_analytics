"""Fundamentals fetcher. yfinance primary; FD API can extend later."""
from datetime import datetime

import pandas as pd
import yfinance as yf

from stock_analytics.briefing.schema import FundamentalsData


def _get(df: pd.DataFrame | None, row: str, col_index: int = 0) -> float | None:
    if df is None or df.empty or row not in df.index:
        return None
    try:
        val = df.loc[row].iloc[col_index]
        return float(val) if pd.notna(val) else None
    except (IndexError, KeyError, TypeError, ValueError):
        return None


def _ttm_sum(quarterly: pd.DataFrame | None, row: str) -> float | None:
    """Sum the most recent 4 quarters for a row."""
    if quarterly is None or quarterly.empty or row not in quarterly.index:
        return None
    try:
        vals = quarterly.loc[row].iloc[:4]
        if vals.isna().any():
            return None
        return float(vals.sum())
    except (KeyError, TypeError, ValueError):
        return None


def fetch_fundamentals(ticker: str, fetched_at: datetime) -> FundamentalsData:
    t = yf.Ticker(ticker)
    info = t.info or {}
    inc = t.income_stmt
    inc_q = t.quarterly_income_stmt
    bs = t.balance_sheet
    cf = t.cashflow

    # Annual income statement: most recent column = current year
    revenue_ttm = _ttm_sum(inc_q, "Total Revenue") or _get(inc, "Total Revenue", 0)
    revenue_prior_ttm = _get(inc, "Total Revenue", 1)
    revenue_3y_ago = _get(inc, "Total Revenue", 3)

    # Book value: prefer Stockholders Equity from balance sheet
    book_value = _get(bs, "Stockholders Equity", 0)
    if book_value is None:
        bv_per_share = info.get("bookValue")
        shares = info.get("sharesOutstanding")
        if bv_per_share and shares:
            book_value = bv_per_share * shares

    return FundamentalsData(
        revenue_ttm=revenue_ttm,
        revenue_prior_ttm=revenue_prior_ttm,
        revenue_3y_ago=revenue_3y_ago,
        gross_profit_ttm=_ttm_sum(inc_q, "Gross Profit") or _get(inc, "Gross Profit", 0),
        operating_income_ttm=_ttm_sum(inc_q, "Operating Income") or _get(inc, "Operating Income", 0),
        net_income_ttm=_ttm_sum(inc_q, "Net Income") or _get(inc, "Net Income", 0),
        free_cash_flow_ttm=_ttm_sum(t.quarterly_cashflow, "Free Cash Flow") or _get(cf, "Free Cash Flow", 0),
        total_debt=_get(bs, "Total Debt", 0) or info.get("totalDebt"),
        cash_and_equivalents=_get(bs, "Cash And Cash Equivalents", 0) or info.get("totalCash"),
        ebitda_ttm=info.get("ebitda"),
        shares_outstanding=info.get("sharesOutstanding"),
        book_value=book_value,
        earnings_beat_streak=0,  # yfinance doesn't expose this cleanly; v1 leaves 0
        source="yfinance",
        fetched_at=fetched_at,
    )
