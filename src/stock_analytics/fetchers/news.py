"""News fetcher using yfinance's built-in news feed."""
from datetime import datetime, timezone

import yfinance as yf

from stock_analytics.briefing.schema import NewsData, NewsItem
from stock_analytics.utils.timeguard import ensure_et


def fetch_news(ticker: str, fetched_at: datetime, limit: int = 10) -> NewsData:
    t = yf.Ticker(ticker)
    items: list[NewsItem] = []
    try:
        news = t.news or []
        for entry in news[:limit]:
            ts = entry.get("providerPublishTime")
            if ts is None:
                continue
            date = datetime.fromtimestamp(ts, tz=timezone.utc)
            items.append(NewsItem(
                date=ensure_et(date),
                headline=entry.get("title", ""),
                source=entry.get("publisher", "unknown"),
                url=entry.get("link"),
                sentiment="neutral",  # v1 doesn't classify; leave neutral
            ))
    except Exception:
        pass

    return NewsData(items=items, source="yfinance", fetched_at=fetched_at)
