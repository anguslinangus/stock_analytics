"""Pydantic models — the data contract between fetchers, indicators, scoring, and briefing."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# ---------- Raw data from fetchers ----------

class PricePoint(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

class PriceData(BaseModel):
    history: list[PricePoint]
    source: str
    fetched_at: datetime

class FundamentalsData(BaseModel):
    # TTM and historical financials
    revenue_ttm: float | None = None
    revenue_prior_ttm: float | None = None
    revenue_3y_ago: float | None = None
    gross_profit_ttm: float | None = None
    operating_income_ttm: float | None = None
    net_income_ttm: float | None = None
    free_cash_flow_ttm: float | None = None
    total_debt: float | None = None
    cash_and_equivalents: float | None = None
    ebitda_ttm: float | None = None
    shares_outstanding: float | None = None
    book_value: float | None = None
    earnings_beat_streak: int = 0  # consecutive quarters of EPS beat
    source: str
    fetched_at: datetime

class OwnershipData(BaseModel):
    institutional_pct: float | None = None
    institutional_pct_change_qoq: float | None = None
    insider_net_buying_90d: float | None = None  # negative = selling
    source: str
    fetched_at: datetime

class AnalystEntry(BaseModel):
    date: datetime
    firm: str
    action: str  # e.g. "Upgrade", "Downgrade", "Initiate"
    from_grade: str | None = None
    to_grade: str | None = None

class AnalystData(BaseModel):
    consensus: str | None = None  # BUY / HOLD / SELL
    target_mean: float | None = None
    target_high: float | None = None
    target_low: float | None = None
    num_buy: int = 0
    num_hold: int = 0
    num_sell: int = 0
    recent_revisions: list[AnalystEntry] = Field(default_factory=list)
    source: str
    fetched_at: datetime

class NewsItem(BaseModel):
    date: datetime
    headline: str
    source: str
    url: str | None = None
    sentiment: Literal["bullish", "bearish", "neutral"] = "neutral"

class NewsData(BaseModel):
    items: list[NewsItem]
    source: str
    fetched_at: datetime

class CompanySnapshot(BaseModel):
    ticker: str
    name: str
    sector: str | None = None
    industry: str | None = None
    market_cap: float | None = None
    current_price: float
    week52_high: float | None = None
    week52_low: float | None = None
    avg_volume_20d: float | None = None

class RawData(BaseModel):
    snapshot: CompanySnapshot
    price: PriceData
    fundamentals: FundamentalsData
    ownership: OwnershipData
    analyst: AnalystData
    news: NewsData
    as_of: datetime

# ---------- Computed indicators ----------

class FundamentalsIndicators(BaseModel):
    revenue_growth_yoy: float | None = None
    revenue_cagr_3y: float | None = None
    gross_margin: float | None = None
    operating_margin: float | None = None
    net_margin: float | None = None
    fcf_margin: float | None = None
    fcf_to_net_income: float | None = None
    roe: float | None = None
    net_debt_to_ebitda: float | None = None
    earnings_beat_streak: int = 0

class ValuationIndicators(BaseModel):
    pe_ttm: float | None = None
    pe_forward: float | None = None
    peg: float | None = None
    ev_ebitda: float | None = None
    ps: float | None = None
    pb: float | None = None
    dcf_fair_value: float | None = None
    dcf_upside_pct: float | None = None
    dcf_assumptions: dict = Field(default_factory=dict)
    industry_pe_median: float | None = None
    industry_ev_ebitda_median: float | None = None

class TechnicalsIndicators(BaseModel):
    sma_50: float | None = None
    sma_200: float | None = None
    price_vs_sma50_pct: float | None = None
    price_vs_sma200_pct: float | None = None
    golden_cross: bool = False
    death_cross: bool = False
    rsi_14: float | None = None
    macd_signal: Literal["positive", "negative", "neutral"] = "neutral"
    volume_20d_vs_60d_pct: float | None = None
    distance_from_52w_high_pct: float | None = None

class Indicators(BaseModel):
    fundamentals: FundamentalsIndicators
    valuation: ValuationIndicators
    technicals: TechnicalsIndicators

# ---------- Scoring ----------

class DimensionScore(BaseModel):
    value: float = Field(ge=0, le=10)
    hits: list[str]

class CompositeScore(BaseModel):
    fundamentals: DimensionScore
    valuation: DimensionScore
    technicals: DimensionScore
    sentiment: DimensionScore
    weights: dict[str, float] = Field(
        default_factory=lambda: {
            "fundamentals": 0.30,
            "valuation": 0.30,
            "technicals": 0.20,
            "sentiment": 0.20,
        }
    )
    composite: float

class RedFlag(BaseModel):
    severity: Literal["info", "warn", "critical"]
    code: str
    message: str

# ---------- Final assembled briefing ----------

class ScoredBriefing(BaseModel):
    raw: RawData
    indicators: Indicators
    scores: CompositeScore
    red_flags: list[RedFlag]
    as_of: datetime
