"""Ownership data: institutional %, insider transactions."""
from datetime import datetime

import pandas as pd
import yfinance as yf

from stock_analytics.briefing.schema import OwnershipData


def fetch_ownership(ticker: str, fetched_at: datetime) -> OwnershipData:
    t = yf.Ticker(ticker)
    info = t.info or {}

    institutional_pct = info.get("heldPercentInstitutions")

    insider_net = None
    try:
        txns = t.insider_transactions
        if isinstance(txns, pd.DataFrame) and not txns.empty:
            recent = txns.head(20)  # most recent
            if "Value" in recent.columns and "Transaction" in recent.columns:
                buys = recent[recent["Transaction"].str.contains("Buy", case=False, na=False)]["Value"].sum()
                sells = recent[recent["Transaction"].str.contains("Sale", case=False, na=False)]["Value"].sum()
                insider_net = float(buys - sells)
    except Exception:
        pass

    return OwnershipData(
        institutional_pct=institutional_pct,
        institutional_pct_change_qoq=None,  # yfinance doesn't expose; v1 leaves None
        insider_net_buying_90d=insider_net,
        source="yfinance",
        fetched_at=fetched_at,
    )
