"""Manual smoke test. Hits live APIs. Run after dependency changes."""
from __future__ import annotations

from rich.console import Console

from stock_analytics.cli import analyze
from stock_analytics.fetchers.analyst import fetch_analyst
from stock_analytics.fetchers.fundamentals import fetch_fundamentals
from stock_analytics.fetchers.news import fetch_news
from stock_analytics.fetchers.ownership import fetch_ownership
from stock_analytics.fetchers.price import fetch_price_and_snapshot
from stock_analytics.utils.timeguard import now_et

console = Console()

TICKERS = ["AAPL", "NVDA", "BRK-B"]


def smoke_fetchers():
    console.rule("Fetcher smoke")
    for t in TICKERS:
        n = now_et()
        try:
            snap, price = fetch_price_and_snapshot(t, n)
            fund = fetch_fundamentals(t, n)
            own = fetch_ownership(t, n)
            an = fetch_analyst(t, n)
            news = fetch_news(t, n)
            console.print(
                f"[green]✓[/green] {t}: price={snap.current_price:.2f} bars={len(price.history)} "
                f"rev_ttm={fund.revenue_ttm} inst%={own.institutional_pct} "
                f"target={an.target_mean} news={len(news.items)}"
            )
        except Exception as e:
            console.print(f"[red]✗[/red] {t}: {type(e).__name__}: {e}")


def smoke_pipeline():
    console.rule("End-to-end pipeline")
    for t in TICKERS:
        try:
            json_path, brief_path = analyze(t)
            console.print(f"[green]✓[/green] {t}: {brief_path}")
        except Exception as e:
            console.print(f"[red]✗[/red] {t}: {type(e).__name__}: {e}")


if __name__ == "__main__":
    smoke_fetchers()
    smoke_pipeline()
