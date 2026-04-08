"""Technicals: SMA, RSI, MACD, volume, 52W. Pure functions over RawData."""
from typing import Literal

import numpy as np
import pandas as pd

from stock_analytics.briefing.schema import RawData, TechnicalsIndicators


def _to_series(raw: RawData) -> pd.Series | None:
    if not raw.price.history:
        return None
    return pd.Series([p.close for p in raw.price.history])


def _sma(s: pd.Series, window: int) -> float | None:
    if len(s) < window:
        return None
    return float(s.rolling(window).mean().iloc[-1])


def _rsi(s: pd.Series, period: int = 14) -> float | None:
    if len(s) < period + 1:
        return None
    delta = s.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    val = rsi.iloc[-1]
    return float(val) if pd.notna(val) else None


def _macd_signal(s: pd.Series) -> Literal["positive", "negative", "neutral"]:
    if len(s) < 35:
        return "neutral"
    ema12 = s.ewm(span=12, adjust=False).mean()
    ema26 = s.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    diff = macd.iloc[-1] - signal.iloc[-1]
    if diff > 0:
        return "positive"
    if diff < 0:
        return "negative"
    return "neutral"


def compute_technicals_indicators(raw: RawData) -> TechnicalsIndicators:
    s = _to_series(raw)
    if s is None or len(s) == 0:
        return TechnicalsIndicators()

    sma50 = _sma(s, 50)
    sma200 = _sma(s, 200)
    current = float(s.iloc[-1])

    price_vs_sma50 = (current - sma50) / sma50 if sma50 else None
    price_vs_sma200 = (current - sma200) / sma200 if sma200 else None
    golden = bool(sma50 and sma200 and sma50 > sma200)
    death = bool(sma50 and sma200 and sma50 < sma200)

    rsi = _rsi(s, 14)
    macd = _macd_signal(s)

    # Volume comparison
    volumes = pd.Series([p.volume for p in raw.price.history])
    vol_pct = None
    if len(volumes) >= 60:
        vol20 = volumes.tail(20).mean()
        vol60 = volumes.tail(60).mean()
        vol_pct = float((vol20 - vol60) / vol60) if vol60 else None

    # Distance from 52W high
    dist_52w_high = None
    if raw.snapshot.week52_high and raw.snapshot.week52_high > 0:
        dist_52w_high = (current - raw.snapshot.week52_high) / raw.snapshot.week52_high

    return TechnicalsIndicators(
        sma_50=sma50,
        sma_200=sma200,
        price_vs_sma50_pct=price_vs_sma50,
        price_vs_sma200_pct=price_vs_sma200,
        golden_cross=golden,
        death_cross=death,
        rsi_14=rsi,
        macd_signal=macd,
        volume_20d_vs_60d_pct=vol_pct,
        distance_from_52w_high_pct=dist_52w_high,
    )
