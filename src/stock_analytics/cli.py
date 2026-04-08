"""CLI entry point. One run = one ticker analysis."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console

from stock_analytics.briefing.builder import build_briefing_markdown
from stock_analytics.briefing.schema import (
    Indicators, RawData, ScoredBriefing,
)
from stock_analytics.fetchers.analyst import fetch_analyst
from stock_analytics.fetchers.fundamentals import fetch_fundamentals
from stock_analytics.fetchers.news import fetch_news
from stock_analytics.fetchers.ownership import fetch_ownership
from stock_analytics.fetchers.price import fetch_price_and_snapshot
from stock_analytics.indicators.fundamentals import compute_fundamentals_indicators
from stock_analytics.indicators.technicals import compute_technicals_indicators
from stock_analytics.indicators.valuation import compute_valuation_indicators
from stock_analytics.scoring.red_flags import detect_red_flags
from stock_analytics.scoring.rubric import compose
from stock_analytics.utils.cache import cache_path, read_cache, write_cache
from stock_analytics.utils.timeguard import now_et

console = Console()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


def fetch_all(ticker: str, as_of: datetime) -> RawData:
    snapshot, price = fetch_price_and_snapshot(ticker, as_of)
    fundamentals = fetch_fundamentals(ticker, as_of)
    ownership = fetch_ownership(ticker, as_of)
    analyst = fetch_analyst(ticker, as_of)
    news = fetch_news(ticker, as_of)
    return RawData(
        snapshot=snapshot, price=price, fundamentals=fundamentals,
        ownership=ownership, analyst=analyst, news=news, as_of=as_of,
    )


def analyze(ticker: str) -> tuple[Path, Path]:
    """Run one analysis. Returns (json_path, briefing_md_path)."""
    ticker = ticker.upper()
    as_of = now_et()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Check cache
    cached = read_cache(ticker, as_of, DATA_DIR)
    if cached:
        console.print(f"[dim]Cache hit for {ticker}[/dim]")
        raw = RawData.model_validate(cached)
    else:
        console.print(f"[bold]Fetching {ticker}...[/bold]")
        raw = fetch_all(ticker, as_of)
        write_cache(ticker, as_of, raw.model_dump(mode="json"), DATA_DIR)

    # Indicators
    indicators = Indicators(
        fundamentals=compute_fundamentals_indicators(raw),
        valuation=compute_valuation_indicators(raw),
        technicals=compute_technicals_indicators(raw),
    )

    # Scoring
    scores = compose(indicators, raw.analyst, raw.ownership)
    red_flags = detect_red_flags(raw, indicators)

    scored = ScoredBriefing(
        raw=raw, indicators=indicators, scores=scores,
        red_flags=red_flags, as_of=as_of,
    )

    # Write briefing
    json_path = cache_path(ticker, as_of, DATA_DIR)
    briefing_path = json_path.with_name(f"{ticker}_{as_of.strftime('%Y-%m-%d')}_briefing.md")
    briefing_path.write_text(build_briefing_markdown(scored))

    console.print(f"[green]✓[/green] Briefing: {briefing_path}")
    console.print(f"[green]✓[/green] Composite score: {scores.composite:.2f} / 10")
    return json_path, briefing_path


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="stock_analytics",
        description="Fetch, compute, and score US-equity data into a briefing for Claude.",
    )
    parser.add_argument("ticker", help="US stock ticker, e.g. NVDA")
    args = parser.parse_args()

    try:
        analyze(args.ticker)
        return 0
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        return 1
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {type(e).__name__}: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
