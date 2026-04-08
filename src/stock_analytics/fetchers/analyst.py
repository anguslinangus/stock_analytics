"""Analyst ratings, targets, recent revisions."""
from datetime import datetime

import pandas as pd
import yfinance as yf

from stock_analytics.briefing.schema import AnalystData, AnalystEntry
from stock_analytics.utils.timeguard import ensure_et


def fetch_analyst(ticker: str, fetched_at: datetime) -> AnalystData:
    t = yf.Ticker(ticker)
    info = t.info or {}

    rec = None
    try:
        rec = t.recommendations
    except Exception:
        pass

    revisions: list[AnalystEntry] = []
    num_buy = num_hold = num_sell = 0

    if isinstance(rec, pd.DataFrame) and not rec.empty:
        # Most recent rows
        recent = rec.tail(20) if len(rec) > 20 else rec
        for _, row in recent.iterrows():
            try:
                date = row.name if hasattr(row, "name") and isinstance(row.name, pd.Timestamp) else None
                if date is None:
                    continue
                revisions.append(AnalystEntry(
                    date=ensure_et(date.to_pydatetime()),
                    firm=str(row.get("Firm", "")),
                    action=str(row.get("Action", "")),
                    from_grade=row.get("From Grade"),
                    to_grade=row.get("To Grade"),
                ))
            except Exception:
                continue

    consensus = (info.get("recommendationKey") or "").upper() or None
    if consensus == "STRONG_BUY":
        consensus = "BUY"

    num_analysts = info.get("numberOfAnalystOpinions", 0) or 0

    return AnalystData(
        consensus=consensus,
        target_mean=info.get("targetMeanPrice"),
        target_high=info.get("targetHighPrice"),
        target_low=info.get("targetLowPrice"),
        num_buy=num_analysts if consensus == "BUY" else 0,
        num_hold=num_analysts if consensus == "HOLD" else 0,
        num_sell=num_analysts if consensus == "SELL" else 0,
        recent_revisions=revisions[-5:],
        source="yfinance",
        fetched_at=fetched_at,
    )
