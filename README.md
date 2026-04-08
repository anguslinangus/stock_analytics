# Stock Analytics

Personal US-equity analysis tool. **Python computes the numbers, Claude Code narrates, you decide.**

Inspired by `virattt/ai-hedge-fund` but deliberately simpler: no agent persona role-play, no LLM-generated numbers, no auto buy/sell signals. The tool produces a structured briefing and Claude turns it into a report you can interrogate.

See `docs/specs/2026-04-09-stock-analytics-design.md` for the full design rationale.

## Setup

```bash
git clone https://github.com/anguslinangus/stock_analytics.git
cd stock_analytics
uv sync
cp .env.example .env  # (optional, only needed for Financial Datasets API)
```

## Usage

### Via Claude Code (recommended)

In a Claude Code session opened in this project:

```
/analyze NVDA
```

Claude will:
1. Run the Python data engine to fetch and score
2. Read the briefing + prompt rules
3. Display a short report inline
4. Save a long report to `reports/`
5. Wait for follow-up questions (no re-fetch needed)

### Via terminal (briefing only)

```bash
uv run python -m stock_analytics NVDA
```

Produces `data/NVDA_<today>.json` and `data/NVDA_<today>_briefing.md`. No analysis report — that's Claude's job.

## How it works

Three layers, each with one job:

1. **`src/stock_analytics/`** — Python: fetch raw data, compute indicators, score, build briefing
2. **`prompts/`** — instructions for how Claude must analyze (no fabrication, both sides required)
3. **Claude Code** — reads briefing, produces narrative reports, answers follow-ups

## Tests

```bash
uv run pytest
```

Indicator math, scoring rubric, and briefing builder are unit-tested. Fetchers are smoke-tested manually:

```bash
uv run python scripts/smoke_test.py
```

## What it does NOT do

- Real trading or order generation
- Backtesting
- Portfolio analytics
- Non-US equities, options, crypto
- Auto-push to Telegram (use Claude cowork to forward reports manually)

This is a personal research tool, not investment advice. See spec §15 for success criteria.
