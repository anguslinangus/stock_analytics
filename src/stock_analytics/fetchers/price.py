"""Price + snapshot fetcher using yfinance."""
from datetime import datetime

import yfinance as yf

from stock_analytics.briefing.schema import CompanySnapshot, PriceData, PricePoint
from stock_analytics.utils.timeguard import ensure_et


def fetch_price_and_snapshot(ticker: str, fetched_at: datetime) -> tuple[CompanySnapshot, PriceData]:
    yf_ticker = yf.Ticker(ticker)
    info = yf_ticker.info or {}
    hist = yf_ticker.history(period="2y", auto_adjust=True)

    if hist.empty:
        raise ValueError(f"No price history for {ticker}. Ticker may be invalid.")

    points: list[PricePoint] = []
    for idx, row in hist.iterrows():
        points.append(PricePoint(
            date=ensure_et(idx.to_pydatetime() if hasattr(idx, "to_pydatetime") else idx),
            open=float(row["Open"]),
            high=float(row["High"]),
            low=float(row["Low"]),
            close=float(row["Close"]),
            volume=int(row["Volume"]),
        ))

    snapshot = CompanySnapshot(
        ticker=ticker.upper(),
        name=info.get("longName") or info.get("shortName") or ticker.upper(),
        sector=info.get("sector"),
        industry=info.get("industry"),
        market_cap=info.get("marketCap"),
        current_price=float(points[-1].close),
        week52_high=info.get("fiftyTwoWeekHigh"),
        week52_low=info.get("fiftyTwoWeekLow"),
        avg_volume_20d=info.get("averageVolume10days") or info.get("averageVolume"),
    )

    price = PriceData(history=points, source="yfinance", fetched_at=fetched_at)
    return snapshot, price
