# Stock Analytics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CLI tool that fetches US-equity data, computes financial/technical indicators, scores them on four dimensions, and assembles a structured briefing markdown that Claude Code consumes via a `/analyze TICKER` slash command to produce short and long analyst reports.

**Architecture:** Three layers — (1) Python data engine: pure functions for fetch → indicators → scoring → briefing assembly, (2) prompt templates with hard rules forbidding number generation, (3) Claude Code as the orchestrator and analyst, invoked via slash command. Reports save to `reports/`, indexed in a CSV for history.

**Tech Stack:** Python 3.11+, uv for package management, yfinance + Financial Datasets API for data, pandas/numpy for computation, Pydantic v2 for schemas, pytest for tests, rich for CLI output.

**Project root:** `/Users/anguslin/Documents/Claude_Agents/Stock_Analytics`

**Spec:** `docs/specs/2026-04-09-stock-analytics-design.md`

---

## Conventions used in this plan

- All paths are relative to the project root unless stated otherwise.
- Every task ends with a commit step. Commit messages use Conventional Commits.
- TDD discipline: failing test → run (verify red) → minimal impl → run (verify green) → commit.
- Fetchers do **not** get unit tests (per spec §10). They get a manual smoke script.
- All public functions have type hints. Pydantic models are the data contract between layers.
- "as_of" datetime is passed explicitly through every layer — never use `datetime.now()` deep in the call stack.

---

## File Structure (locked in before tasks)

```
Stock_Analytics/
├── pyproject.toml
├── .env.example
├── .gitignore
├── README.md
├── src/stock_analytics/
│   ├── __init__.py
│   ├── __main__.py                 # enables `python -m stock_analytics`
│   ├── cli.py                      # CLI entry, argparse, orchestrates one analysis run
│   ├── fetchers/
│   │   ├── __init__.py
│   │   ├── price.py
│   │   ├── fundamentals.py
│   │   ├── ownership.py
│   │   ├── analyst.py
│   │   └── news.py
│   ├── indicators/
│   │   ├── __init__.py
│   │   ├── fundamentals.py
│   │   ├── valuation.py
│   │   ├── technicals.py
│   │   └── peers.py
│   ├── scoring/
│   │   ├── __init__.py
│   │   ├── rubric.py
│   │   └── red_flags.py
│   ├── briefing/
│   │   ├── __init__.py
│   │   ├── schema.py               # Pydantic models: RawData, Indicators, ScoredBriefing
│   │   └── builder.py              # ScoredBriefing → markdown
│   └── utils/
│       ├── __init__.py
│       ├── cache.py
│       └── timeguard.py
├── prompts/
│   ├── rules.md
│   ├── analyst_short.md
│   └── analyst_full.md
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # shared fixtures (sample raw data)
│   ├── fixtures/
│   │   └── sample_nvda.json        # canned RawData for deterministic tests
│   ├── test_timeguard.py
│   ├── test_cache.py
│   ├── test_indicators_fundamentals.py
│   ├── test_indicators_valuation.py
│   ├── test_indicators_technicals.py
│   ├── test_scoring_rubric.py
│   ├── test_red_flags.py
│   └── test_briefing_builder.py
├── scripts/
│   └── smoke_test.py               # manual: hit live APIs, print summary
├── data/                           # gitignored, populated at runtime
├── reports/                        # gitignored, populated at runtime
└── .claude/
    └── commands/
        └── analyze.md
```

---

## Task 1: Project scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `README.md`
- Create: `src/stock_analytics/__init__.py`
- Create: `src/stock_analytics/__main__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Initialize git repo**

```bash
cd /Users/anguslin/Documents/Claude_Agents/Stock_Analytics
git init
```

- [ ] **Step 2: Create `.gitignore`**

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
.pytest_cache/
.coverage
htmlcov/

# Project
data/
reports/
.env

# OS
.DS_Store
```

- [ ] **Step 3: Create `pyproject.toml`**

```toml
[project]
name = "stock-analytics"
version = "0.1.0"
description = "Personal US-equity analysis tool — Python computes, Claude narrates."
requires-python = ">=3.11"
dependencies = [
    "yfinance>=0.2.40",
    "pandas>=2.2",
    "numpy>=1.26",
    "pydantic>=2.6",
    "httpx>=0.27",
    "python-dotenv>=1.0",
    "rich>=13.7",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/stock_analytics"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v"
```

- [ ] **Step 4: Create `.env.example`**

```
# Optional. Falls back to yfinance-only if absent.
FINANCIAL_DATASETS_API_KEY=
```

- [ ] **Step 5: Create empty package files**

`src/stock_analytics/__init__.py`:
```python
"""Stock Analytics — Python computes, Claude narrates."""
__version__ = "0.1.0"
```

`src/stock_analytics/__main__.py`:
```python
from stock_analytics.cli import main

if __name__ == "__main__":
    main()
```

`tests/__init__.py`: empty file.

`tests/conftest.py`:
```python
"""Shared fixtures for tests. Real fixtures added in later tasks."""
```

- [ ] **Step 6: Create stub `cli.py` so package installs**

`src/stock_analytics/cli.py`:
```python
def main() -> int:
    """CLI entry point. Implemented in Task 16."""
    raise NotImplementedError("CLI not yet implemented")
```

- [ ] **Step 7: Create `README.md`**

```markdown
# Stock Analytics

Personal US-equity analysis tool. Python computes the numbers, Claude Code narrates.

See `docs/specs/2026-04-09-stock-analytics-design.md` for the full design.

## Quick start

```bash
uv sync
uv run python -m stock_analytics NVDA
```

Then in Claude Code: `/analyze NVDA`
```

- [ ] **Step 8: Install dependencies and verify**

```bash
uv sync
uv run python -c "import stock_analytics; print(stock_analytics.__version__)"
```

Expected: `0.1.0`

- [ ] **Step 9: Commit**

```bash
git add .gitignore pyproject.toml .env.example README.md src tests
git commit -m "chore: initial project scaffold"
```

---

## Task 2: Pydantic schema

**Files:**
- Create: `src/stock_analytics/briefing/__init__.py`
- Create: `src/stock_analytics/briefing/schema.py`

These models are the data contract for every layer below. Define them once, use everywhere.

- [ ] **Step 1: Create empty `__init__.py`**

`src/stock_analytics/briefing/__init__.py`: empty.

- [ ] **Step 2: Create `schema.py` with all Pydantic models**

`src/stock_analytics/briefing/schema.py`:
```python
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
```

- [ ] **Step 3: Verify import**

```bash
uv run python -c "from stock_analytics.briefing.schema import ScoredBriefing; print('ok')"
```

Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add src/stock_analytics/briefing/
git commit -m "feat(schema): define pydantic models for raw/indicators/scores/briefing"
```

---

## Task 3: Timeguard utility

**Files:**
- Create: `src/stock_analytics/utils/__init__.py`
- Create: `src/stock_analytics/utils/timeguard.py`
- Create: `tests/test_timeguard.py`

The timeguard ensures every datetime in the system is timezone-aware (US/Eastern, where US markets live) and that an explicit `as_of` is threaded through, never `datetime.now()` deep in code.

- [ ] **Step 1: Create `__init__.py`**

`src/stock_analytics/utils/__init__.py`: empty.

- [ ] **Step 2: Write the failing test**

`tests/test_timeguard.py`:
```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from stock_analytics.utils.timeguard import now_et, ensure_et, format_as_of


def test_now_et_returns_timezone_aware():
    result = now_et()
    assert result.tzinfo is not None
    assert result.tzinfo == ZoneInfo("America/New_York")


def test_ensure_et_converts_naive_to_et():
    naive = datetime(2026, 4, 9, 12, 0, 0)
    result = ensure_et(naive)
    assert result.tzinfo == ZoneInfo("America/New_York")


def test_ensure_et_converts_utc_to_et():
    utc = datetime(2026, 4, 9, 16, 0, 0, tzinfo=timezone.utc)
    result = ensure_et(utc)
    assert result.tzinfo == ZoneInfo("America/New_York")
    assert result.hour == 12  # EDT offset in April


def test_format_as_of_renders_human_readable():
    dt = datetime(2026, 4, 9, 16, 0, 0, tzinfo=ZoneInfo("America/New_York"))
    assert format_as_of(dt) == "2026-04-09 16:00 ET"
```

- [ ] **Step 3: Run test, expect failure**

```bash
uv run pytest tests/test_timeguard.py -v
```

Expected: ImportError or ModuleNotFoundError for `stock_analytics.utils.timeguard`.

- [ ] **Step 4: Implement `timeguard.py`**

`src/stock_analytics/utils/timeguard.py`:
```python
"""Timezone discipline. All datetimes in the system are US/Eastern, timezone-aware."""
from datetime import datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")


def now_et() -> datetime:
    """Current time in US/Eastern. Use this once at the top of a run; thread `as_of` after."""
    return datetime.now(ET)


def ensure_et(dt: datetime) -> datetime:
    """Convert any datetime to US/Eastern. Naive datetimes are assumed to be ET."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ET)
    return dt.astimezone(ET)


def format_as_of(dt: datetime) -> str:
    """Render a datetime as the canonical 'YYYY-MM-DD HH:MM ET' header string."""
    et = ensure_et(dt)
    return et.strftime("%Y-%m-%d %H:%M ET")
```

- [ ] **Step 5: Run tests, expect pass**

```bash
uv run pytest tests/test_timeguard.py -v
```

Expected: 4 passed.

- [ ] **Step 6: Commit**

```bash
git add src/stock_analytics/utils/__init__.py src/stock_analytics/utils/timeguard.py tests/test_timeguard.py
git commit -m "feat(utils): add timeguard for timezone-aware datetime handling"
```

---

## Task 4: Cache utility

**Files:**
- Create: `src/stock_analytics/utils/cache.py`
- Create: `tests/test_cache.py`

Cache reads/writes raw data JSON keyed by ticker + date. Same-day re-runs hit cache.

- [ ] **Step 1: Write the failing test**

`tests/test_cache.py`:
```python
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from stock_analytics.utils.cache import cache_path, read_cache, write_cache


def test_cache_path_format(tmp_path):
    p = cache_path("NVDA", datetime(2026, 4, 9, tzinfo=ZoneInfo("America/New_York")), root=tmp_path)
    assert p == tmp_path / "NVDA_2026-04-09.json"


def test_write_then_read_roundtrip(tmp_path):
    payload = {"ticker": "NVDA", "value": 42}
    as_of = datetime(2026, 4, 9, tzinfo=ZoneInfo("America/New_York"))
    write_cache("NVDA", as_of, payload, root=tmp_path)
    result = read_cache("NVDA", as_of, root=tmp_path)
    assert result == payload


def test_read_cache_missing_returns_none(tmp_path):
    as_of = datetime(2026, 4, 9, tzinfo=ZoneInfo("America/New_York"))
    assert read_cache("NVDA", as_of, root=tmp_path) is None


def test_write_cache_creates_root_if_missing(tmp_path):
    nested = tmp_path / "data"
    as_of = datetime(2026, 4, 9, tzinfo=ZoneInfo("America/New_York"))
    write_cache("NVDA", as_of, {"x": 1}, root=nested)
    assert (nested / "NVDA_2026-04-09.json").exists()
```

- [ ] **Step 2: Run test, expect failure**

```bash
uv run pytest tests/test_cache.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `cache.py`**

`src/stock_analytics/utils/cache.py`:
```python
"""On-disk JSON cache keyed by ticker + ET date. One file per (ticker, day)."""
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from stock_analytics.utils.timeguard import ensure_et


def cache_path(ticker: str, as_of: datetime, root: Path) -> Path:
    et = ensure_et(as_of)
    return root / f"{ticker.upper()}_{et.strftime('%Y-%m-%d')}.json"


def read_cache(ticker: str, as_of: datetime, root: Path) -> dict[str, Any] | None:
    path = cache_path(ticker, as_of, root)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def write_cache(ticker: str, as_of: datetime, payload: dict[str, Any], root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = cache_path(ticker, as_of, root)
    path.write_text(json.dumps(payload, indent=2, default=str))
    return path
```

- [ ] **Step 4: Run tests, expect pass**

```bash
uv run pytest tests/test_cache.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/stock_analytics/utils/cache.py tests/test_cache.py
git commit -m "feat(utils): add JSON cache keyed by ticker and ET date"
```

---

## Task 5: Test fixtures (canned NVDA data)

**Files:**
- Create: `tests/fixtures/sample_nvda.json`
- Modify: `tests/conftest.py`

Indicator and scoring tests need a deterministic raw data fixture so they don't depend on live APIs.

- [ ] **Step 1: Create the fixture file**

`tests/fixtures/sample_nvda.json`:
```json
{
  "snapshot": {
    "ticker": "NVDA",
    "name": "NVIDIA Corporation",
    "sector": "Technology",
    "industry": "Semiconductors",
    "market_cap": 3000000000000,
    "current_price": 900.0,
    "week52_high": 950.0,
    "week52_low": 400.0,
    "avg_volume_20d": 50000000
  },
  "price": {
    "history": [],
    "source": "fixture",
    "fetched_at": "2026-04-09T16:00:00-04:00"
  },
  "fundamentals": {
    "revenue_ttm": 100000000000,
    "revenue_prior_ttm": 60000000000,
    "revenue_3y_ago": 27000000000,
    "gross_profit_ttm": 75000000000,
    "operating_income_ttm": 60000000000,
    "net_income_ttm": 50000000000,
    "free_cash_flow_ttm": 47500000000,
    "total_debt": 10000000000,
    "cash_and_equivalents": 30000000000,
    "ebitda_ttm": 65000000000,
    "shares_outstanding": 2500000000,
    "book_value": 50000000000,
    "earnings_beat_streak": 4,
    "source": "fixture",
    "fetched_at": "2026-04-09T16:00:00-04:00"
  },
  "ownership": {
    "institutional_pct": 0.68,
    "institutional_pct_change_qoq": 0.015,
    "insider_net_buying_90d": -250000000,
    "source": "fixture",
    "fetched_at": "2026-04-09T16:00:00-04:00"
  },
  "analyst": {
    "consensus": "BUY",
    "target_mean": 1050.0,
    "target_high": 1300.0,
    "target_low": 700.0,
    "num_buy": 32,
    "num_hold": 5,
    "num_sell": 1,
    "recent_revisions": [],
    "source": "fixture",
    "fetched_at": "2026-04-09T16:00:00-04:00"
  },
  "news": {
    "items": [],
    "source": "fixture",
    "fetched_at": "2026-04-09T16:00:00-04:00"
  },
  "as_of": "2026-04-09T16:00:00-04:00"
}
```

- [ ] **Step 2: Add fixture loader to `conftest.py`**

`tests/conftest.py`:
```python
"""Shared fixtures for tests."""
import json
from pathlib import Path

import pytest

from stock_analytics.briefing.schema import RawData

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_nvda_raw() -> RawData:
    """Deterministic NVDA RawData for indicator/scoring tests."""
    payload = json.loads((FIXTURES_DIR / "sample_nvda.json").read_text())
    return RawData.model_validate(payload)
```

- [ ] **Step 3: Verify the fixture loads**

```bash
uv run python -c "
import json
from pathlib import Path
from stock_analytics.briefing.schema import RawData
data = json.loads(Path('tests/fixtures/sample_nvda.json').read_text())
raw = RawData.model_validate(data)
print(raw.snapshot.ticker, raw.fundamentals.revenue_ttm)
"
```

Expected: `NVDA 100000000000.0`

- [ ] **Step 4: Commit**

```bash
git add tests/fixtures/sample_nvda.json tests/conftest.py
git commit -m "test: add canned NVDA fixture for deterministic indicator/scoring tests"
```

---

## Task 6: Fundamentals indicators

**Files:**
- Create: `src/stock_analytics/indicators/__init__.py`
- Create: `src/stock_analytics/indicators/fundamentals.py`
- Create: `tests/test_indicators_fundamentals.py`

Pure functions: `RawData → FundamentalsIndicators`. No I/O.

- [ ] **Step 1: Create empty `__init__.py`**

`src/stock_analytics/indicators/__init__.py`: empty.

- [ ] **Step 2: Write the failing tests**

`tests/test_indicators_fundamentals.py`:
```python
import pytest

from stock_analytics.indicators.fundamentals import compute_fundamentals_indicators


def test_revenue_growth_yoy(sample_nvda_raw):
    ind = compute_fundamentals_indicators(sample_nvda_raw)
    # 100B vs 60B prior = 66.67%
    assert ind.revenue_growth_yoy == pytest.approx(0.6667, rel=1e-3)


def test_revenue_cagr_3y(sample_nvda_raw):
    ind = compute_fundamentals_indicators(sample_nvda_raw)
    # (100/27)^(1/3) - 1 ≈ 0.547
    assert ind.revenue_cagr_3y == pytest.approx(0.5475, rel=1e-3)


def test_margins(sample_nvda_raw):
    ind = compute_fundamentals_indicators(sample_nvda_raw)
    assert ind.gross_margin == pytest.approx(0.75)
    assert ind.operating_margin == pytest.approx(0.60)
    assert ind.net_margin == pytest.approx(0.50)
    assert ind.fcf_margin == pytest.approx(0.475)


def test_fcf_to_net_income(sample_nvda_raw):
    ind = compute_fundamentals_indicators(sample_nvda_raw)
    assert ind.fcf_to_net_income == pytest.approx(0.95)


def test_roe(sample_nvda_raw):
    ind = compute_fundamentals_indicators(sample_nvda_raw)
    # 50B / 50B = 1.0
    assert ind.roe == pytest.approx(1.0)


def test_net_debt_to_ebitda_negative_when_net_cash(sample_nvda_raw):
    ind = compute_fundamentals_indicators(sample_nvda_raw)
    # debt 10B - cash 30B = -20B; / 65B EBITDA = -0.308
    assert ind.net_debt_to_ebitda == pytest.approx(-0.3077, rel=1e-3)


def test_handles_missing_fields_gracefully():
    from stock_analytics.briefing.schema import (
        AnalystData, CompanySnapshot, FundamentalsData, NewsData,
        OwnershipData, PriceData, RawData,
    )
    from datetime import datetime
    from zoneinfo import ZoneInfo
    et = ZoneInfo("America/New_York")
    raw = RawData(
        snapshot=CompanySnapshot(ticker="X", name="X", current_price=10.0),
        price=PriceData(history=[], source="t", fetched_at=datetime.now(et)),
        fundamentals=FundamentalsData(source="t", fetched_at=datetime.now(et)),
        ownership=OwnershipData(source="t", fetched_at=datetime.now(et)),
        analyst=AnalystData(source="t", fetched_at=datetime.now(et)),
        news=NewsData(items=[], source="t", fetched_at=datetime.now(et)),
        as_of=datetime.now(et),
    )
    ind = compute_fundamentals_indicators(raw)
    assert ind.revenue_growth_yoy is None
    assert ind.gross_margin is None
```

- [ ] **Step 3: Run tests, expect failure**

```bash
uv run pytest tests/test_indicators_fundamentals.py -v
```

Expected: ImportError.

- [ ] **Step 4: Implement `fundamentals.py`**

`src/stock_analytics/indicators/fundamentals.py`:
```python
"""Pure functions: RawData → FundamentalsIndicators. No I/O."""
from stock_analytics.briefing.schema import FundamentalsIndicators, RawData


def _safe_div(num: float | None, den: float | None) -> float | None:
    if num is None or den is None or den == 0:
        return None
    return num / den


def compute_fundamentals_indicators(raw: RawData) -> FundamentalsIndicators:
    f = raw.fundamentals

    revenue_growth_yoy = None
    if f.revenue_ttm is not None and f.revenue_prior_ttm:
        revenue_growth_yoy = (f.revenue_ttm - f.revenue_prior_ttm) / f.revenue_prior_ttm

    revenue_cagr_3y = None
    if f.revenue_ttm and f.revenue_3y_ago and f.revenue_3y_ago > 0:
        revenue_cagr_3y = (f.revenue_ttm / f.revenue_3y_ago) ** (1 / 3) - 1

    net_debt = None
    if f.total_debt is not None and f.cash_and_equivalents is not None:
        net_debt = f.total_debt - f.cash_and_equivalents

    return FundamentalsIndicators(
        revenue_growth_yoy=revenue_growth_yoy,
        revenue_cagr_3y=revenue_cagr_3y,
        gross_margin=_safe_div(f.gross_profit_ttm, f.revenue_ttm),
        operating_margin=_safe_div(f.operating_income_ttm, f.revenue_ttm),
        net_margin=_safe_div(f.net_income_ttm, f.revenue_ttm),
        fcf_margin=_safe_div(f.free_cash_flow_ttm, f.revenue_ttm),
        fcf_to_net_income=_safe_div(f.free_cash_flow_ttm, f.net_income_ttm),
        roe=_safe_div(f.net_income_ttm, f.book_value),
        net_debt_to_ebitda=_safe_div(net_debt, f.ebitda_ttm),
        earnings_beat_streak=f.earnings_beat_streak,
    )
```

- [ ] **Step 5: Run tests, expect pass**

```bash
uv run pytest tests/test_indicators_fundamentals.py -v
```

Expected: 7 passed.

- [ ] **Step 6: Commit**

```bash
git add src/stock_analytics/indicators/__init__.py src/stock_analytics/indicators/fundamentals.py tests/test_indicators_fundamentals.py
git commit -m "feat(indicators): compute fundamentals indicators with null-safety"
```

---

## Task 7: Valuation indicators (incl. simple DCF)

**Files:**
- Create: `src/stock_analytics/indicators/valuation.py`
- Create: `tests/test_indicators_valuation.py`

DCF uses hard-coded defaults from spec §13: WACC 9%, terminal 3%, 5y growth fade from 25% to 8%.

- [ ] **Step 1: Write the failing tests**

`tests/test_indicators_valuation.py`:
```python
import pytest

from stock_analytics.indicators.valuation import compute_valuation_indicators


def test_pe_ttm(sample_nvda_raw):
    ind = compute_valuation_indicators(sample_nvda_raw)
    # market_cap 3T / net_income 50B = 60
    assert ind.pe_ttm == pytest.approx(60.0)


def test_ps(sample_nvda_raw):
    ind = compute_valuation_indicators(sample_nvda_raw)
    # 3T / 100B = 30
    assert ind.ps == pytest.approx(30.0)


def test_ev_ebitda(sample_nvda_raw):
    ind = compute_valuation_indicators(sample_nvda_raw)
    # EV = 3T + 10B debt - 30B cash = 2980B; /65B EBITDA = 45.85
    assert ind.ev_ebitda == pytest.approx(45.846, rel=1e-3)


def test_pb(sample_nvda_raw):
    ind = compute_valuation_indicators(sample_nvda_raw)
    # 3T / 50B book = 60
    assert ind.pb == pytest.approx(60.0)


def test_dcf_assumptions_recorded(sample_nvda_raw):
    ind = compute_valuation_indicators(sample_nvda_raw)
    assert ind.dcf_assumptions["wacc"] == 0.09
    assert ind.dcf_assumptions["terminal_growth"] == 0.03
    assert ind.dcf_assumptions["growth_path"] == [0.25, 0.20, 0.16, 0.12, 0.08]


def test_dcf_produces_positive_fair_value(sample_nvda_raw):
    ind = compute_valuation_indicators(sample_nvda_raw)
    assert ind.dcf_fair_value is not None
    assert ind.dcf_fair_value > 0
    # upside_pct should be a real number (positive or negative)
    assert ind.dcf_upside_pct is not None
```

- [ ] **Step 2: Run, expect failure**

```bash
uv run pytest tests/test_indicators_valuation.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `valuation.py`**

`src/stock_analytics/indicators/valuation.py`:
```python
"""Valuation indicators including a simple, transparent DCF."""
from stock_analytics.briefing.schema import RawData, ValuationIndicators

# Hard-coded DCF defaults per spec §13. Displayed in briefing for critique.
DCF_WACC = 0.09
DCF_TERMINAL_GROWTH = 0.03
DCF_GROWTH_PATH = [0.25, 0.20, 0.16, 0.12, 0.08]  # 5-year fade
DCF_FCF_MARGIN_CAP = 0.50  # safety: don't extrapolate insane margins


def _safe_div(num, den):
    if num is None or den is None or den == 0:
        return None
    return num / den


def _compute_dcf(raw: RawData) -> tuple[float | None, float | None]:
    """Returns (fair_value_per_share, upside_pct). None if inputs missing."""
    f = raw.fundamentals
    if f.free_cash_flow_ttm is None or f.shares_outstanding is None or f.shares_outstanding == 0:
        return None, None

    fcf = f.free_cash_flow_ttm
    pv_sum = 0.0
    for year, growth in enumerate(DCF_GROWTH_PATH, start=1):
        fcf = fcf * (1 + growth)
        pv_sum += fcf / ((1 + DCF_WACC) ** year)

    # Terminal value at end of forecast horizon
    terminal_fcf = fcf * (1 + DCF_TERMINAL_GROWTH)
    terminal_value = terminal_fcf / (DCF_WACC - DCF_TERMINAL_GROWTH)
    pv_terminal = terminal_value / ((1 + DCF_WACC) ** len(DCF_GROWTH_PATH))

    enterprise_value = pv_sum + pv_terminal
    # Adjust to equity value
    net_debt = (f.total_debt or 0) - (f.cash_and_equivalents or 0)
    equity_value = enterprise_value - net_debt

    fair_value_per_share = equity_value / f.shares_outstanding
    current = raw.snapshot.current_price
    upside_pct = (fair_value_per_share - current) / current if current else None

    return fair_value_per_share, upside_pct


def compute_valuation_indicators(raw: RawData) -> ValuationIndicators:
    s = raw.snapshot
    f = raw.fundamentals

    pe_ttm = _safe_div(s.market_cap, f.net_income_ttm)
    ps = _safe_div(s.market_cap, f.revenue_ttm)
    pb = _safe_div(s.market_cap, f.book_value)

    ev_ebitda = None
    if s.market_cap is not None and f.ebitda_ttm:
        ev = s.market_cap + (f.total_debt or 0) - (f.cash_and_equivalents or 0)
        ev_ebitda = ev / f.ebitda_ttm

    dcf_fv, dcf_up = _compute_dcf(raw)

    return ValuationIndicators(
        pe_ttm=pe_ttm,
        pe_forward=None,  # Requires forward earnings; v1 leaves None
        peg=None,         # Requires forward growth; v1 leaves None
        ev_ebitda=ev_ebitda,
        ps=ps,
        pb=pb,
        dcf_fair_value=dcf_fv,
        dcf_upside_pct=dcf_up,
        dcf_assumptions={
            "wacc": DCF_WACC,
            "terminal_growth": DCF_TERMINAL_GROWTH,
            "growth_path": DCF_GROWTH_PATH,
        },
    )
```

- [ ] **Step 4: Run, expect pass**

```bash
uv run pytest tests/test_indicators_valuation.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add src/stock_analytics/indicators/valuation.py tests/test_indicators_valuation.py
git commit -m "feat(indicators): valuation multiples and simple DCF with explicit assumptions"
```

---

## Task 8: Technicals indicators

**Files:**
- Create: `src/stock_analytics/indicators/technicals.py`
- Create: `tests/test_indicators_technicals.py`

Operates on `raw.price.history`. Tests use synthetic price series so they're deterministic.

- [ ] **Step 1: Write the failing tests**

`tests/test_indicators_technicals.py`:
```python
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from stock_analytics.briefing.schema import (
    AnalystData, CompanySnapshot, FundamentalsData, NewsData,
    OwnershipData, PriceData, PricePoint, RawData,
)
from stock_analytics.indicators.technicals import compute_technicals_indicators

ET = ZoneInfo("America/New_York")


def _make_raw_with_prices(closes: list[float]) -> RawData:
    base = datetime(2025, 1, 1, tzinfo=ET)
    history = [
        PricePoint(
            date=base + timedelta(days=i),
            open=c, high=c * 1.01, low=c * 0.99, close=c, volume=1_000_000,
        )
        for i, c in enumerate(closes)
    ]
    now = datetime(2026, 4, 9, tzinfo=ET)
    return RawData(
        snapshot=CompanySnapshot(
            ticker="T", name="T", current_price=closes[-1],
            week52_high=max(closes), week52_low=min(closes),
        ),
        price=PriceData(history=history, source="t", fetched_at=now),
        fundamentals=FundamentalsData(source="t", fetched_at=now),
        ownership=OwnershipData(source="t", fetched_at=now),
        analyst=AnalystData(source="t", fetched_at=now),
        news=NewsData(items=[], source="t", fetched_at=now),
        as_of=now,
    )


def test_sma_calculation():
    closes = list(range(1, 251))  # 1..250
    raw = _make_raw_with_prices([float(c) for c in closes])
    ind = compute_technicals_indicators(raw)
    # SMA50 = mean of last 50 (201..250) = 225.5
    assert ind.sma_50 == pytest.approx(225.5)
    # SMA200 = mean of last 200 (51..250) = 150.5
    assert ind.sma_200 == pytest.approx(150.5)


def test_price_above_smas():
    closes = [100.0] * 250
    raw = _make_raw_with_prices(closes)
    ind = compute_technicals_indicators(raw)
    assert ind.price_vs_sma50_pct == pytest.approx(0.0)


def test_golden_cross_when_short_above_long():
    closes = list(range(1, 251))
    raw = _make_raw_with_prices([float(c) for c in closes])
    ind = compute_technicals_indicators(raw)
    assert ind.golden_cross is True
    assert ind.death_cross is False


def test_rsi_in_valid_range():
    import math
    closes = [100 + 5 * math.sin(i / 5) for i in range(250)]
    raw = _make_raw_with_prices(closes)
    ind = compute_technicals_indicators(raw)
    assert 0 <= ind.rsi_14 <= 100


def test_distance_from_52w_high():
    closes = [float(c) for c in list(range(1, 250)) + [200]]
    raw = _make_raw_with_prices(closes)
    ind = compute_technicals_indicators(raw)
    # current 200, high 249, distance = (200-249)/249
    assert ind.distance_from_52w_high_pct == pytest.approx(-0.1968, rel=1e-3)


def test_returns_none_for_short_history():
    closes = [100.0] * 10
    raw = _make_raw_with_prices(closes)
    ind = compute_technicals_indicators(raw)
    assert ind.sma_200 is None
    assert ind.sma_50 is None
```

- [ ] **Step 2: Run, expect failure**

```bash
uv run pytest tests/test_indicators_technicals.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `technicals.py`**

`src/stock_analytics/indicators/technicals.py`:
```python
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
```

- [ ] **Step 4: Run, expect pass**

```bash
uv run pytest tests/test_indicators_technicals.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add src/stock_analytics/indicators/technicals.py tests/test_indicators_technicals.py
git commit -m "feat(indicators): SMA/RSI/MACD/volume technicals"
```

---

## Task 9: Peers indicator (industry medians)

**Files:**
- Create: `src/stock_analytics/indicators/peers.py`

For v1, peers data is **not auto-fetched**. The function accepts an optional dict of industry medians (passed in from the fetcher layer if available, else None). This keeps the v1 surface small.

- [ ] **Step 1: Implement `peers.py`**

`src/stock_analytics/indicators/peers.py`:
```python
"""Peer/industry median attachment.

v1: pass-through. The fetcher layer (Task 12) will pull industry medians from
yfinance when possible and inject them via this helper. Indicators stay a pure
function — peers are merged at compose time, not fetched here.
"""
from stock_analytics.briefing.schema import ValuationIndicators


def attach_peer_medians(
    valuation: ValuationIndicators,
    industry_pe_median: float | None,
    industry_ev_ebitda_median: float | None,
) -> ValuationIndicators:
    return valuation.model_copy(
        update={
            "industry_pe_median": industry_pe_median,
            "industry_ev_ebitda_median": industry_ev_ebitda_median,
        }
    )
```

- [ ] **Step 2: Verify import**

```bash
uv run python -c "from stock_analytics.indicators.peers import attach_peer_medians; print('ok')"
```

Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add src/stock_analytics/indicators/peers.py
git commit -m "feat(indicators): peer median attachment helper"
```

---

## Task 10: Scoring rubric

**Files:**
- Create: `src/stock_analytics/scoring/__init__.py`
- Create: `src/stock_analytics/scoring/rubric.py`
- Create: `tests/test_scoring_rubric.py`

Deterministic scoring per spec §8. Each dimension scored independently, then weighted composite.

- [ ] **Step 1: Create empty `__init__.py`**

`src/stock_analytics/scoring/__init__.py`: empty.

- [ ] **Step 2: Write the failing tests**

`tests/test_scoring_rubric.py`:
```python
import pytest

from stock_analytics.briefing.schema import (
    FundamentalsIndicators, Indicators, TechnicalsIndicators, ValuationIndicators,
)
from stock_analytics.scoring.rubric import (
    score_fundamentals, score_valuation, score_technicals, score_sentiment, compose,
)


def test_score_fundamentals_high_growth_high_margin():
    ind = FundamentalsIndicators(
        revenue_growth_yoy=0.50, fcf_margin=0.30, roe=0.40,
        net_debt_to_ebitda=-0.5, earnings_beat_streak=4,
    )
    result = score_fundamentals(ind)
    assert result.value >= 8.0
    assert any("revenue_growth_high" in h for h in result.hits)


def test_score_fundamentals_revenue_declining():
    ind = FundamentalsIndicators(
        revenue_growth_yoy=-0.10, fcf_margin=0.05, roe=0.05,
        net_debt_to_ebitda=3.0,
    )
    result = score_fundamentals(ind)
    assert result.value <= 4.0
    assert any("revenue_declining" in h for h in result.hits)


def test_score_valuation_premium_pe_penalised():
    ind = ValuationIndicators(pe_ttm=80, ps=30, dcf_upside_pct=-0.30)
    result = score_valuation(ind)
    assert result.value <= 4.0


def test_score_valuation_undervalued_dcf():
    ind = ValuationIndicators(pe_ttm=15, ps=2, dcf_upside_pct=0.40)
    result = score_valuation(ind)
    assert result.value >= 7.0


def test_score_technicals_uptrend():
    ind = TechnicalsIndicators(
        price_vs_sma200_pct=0.15, golden_cross=True, rsi_14=58,
        macd_signal="positive", volume_20d_vs_60d_pct=0.10,
    )
    result = score_technicals(ind)
    assert result.value >= 7.0


def test_score_sentiment_strong_buy_consensus():
    from stock_analytics.briefing.schema import AnalystData, OwnershipData
    from datetime import datetime
    from zoneinfo import ZoneInfo
    et = ZoneInfo("America/New_York")
    analyst = AnalystData(
        consensus="BUY", num_buy=30, num_hold=3, num_sell=0,
        source="t", fetched_at=datetime.now(et),
    )
    ownership = OwnershipData(
        institutional_pct_change_qoq=0.02, insider_net_buying_90d=0,
        source="t", fetched_at=datetime.now(et),
    )
    result = score_sentiment(analyst, ownership)
    assert result.value >= 6.5


def test_compose_weighted_average():
    indicators = Indicators(
        fundamentals=FundamentalsIndicators(
            revenue_growth_yoy=0.50, fcf_margin=0.30, roe=0.40,
            net_debt_to_ebitda=-0.5, earnings_beat_streak=4,
        ),
        valuation=ValuationIndicators(pe_ttm=80, ps=30, dcf_upside_pct=-0.30),
        technicals=TechnicalsIndicators(
            price_vs_sma200_pct=0.15, golden_cross=True, rsi_14=58,
            macd_signal="positive", volume_20d_vs_60d_pct=0.10,
        ),
    )
    from stock_analytics.briefing.schema import AnalystData, OwnershipData
    from datetime import datetime
    from zoneinfo import ZoneInfo
    et = ZoneInfo("America/New_York")
    analyst = AnalystData(
        consensus="BUY", num_buy=30, num_hold=3, num_sell=0,
        source="t", fetched_at=datetime.now(et),
    )
    ownership = OwnershipData(
        institutional_pct_change_qoq=0.02, insider_net_buying_90d=0,
        source="t", fetched_at=datetime.now(et),
    )
    composite = compose(indicators, analyst, ownership)
    assert 0 <= composite.composite <= 10
    assert composite.weights["fundamentals"] == 0.30
```

- [ ] **Step 3: Run, expect failure**

```bash
uv run pytest tests/test_scoring_rubric.py -v
```

Expected: ImportError.

- [ ] **Step 4: Implement `rubric.py`**

`src/stock_analytics/scoring/rubric.py`:
```python
"""Deterministic scoring rubric. Each dimension → 0–10 with explicit hit list."""
from stock_analytics.briefing.schema import (
    AnalystData, CompositeScore, DimensionScore, FundamentalsIndicators,
    Indicators, OwnershipData, TechnicalsIndicators, ValuationIndicators,
)


def _clamp(x: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return max(lo, min(hi, x))


def score_fundamentals(ind: FundamentalsIndicators) -> DimensionScore:
    score = 5.0
    hits: list[str] = []

    g = ind.revenue_growth_yoy
    if g is not None:
        if g >= 0.30:
            score += 2.0; hits.append("revenue_growth_high(+2)")
        elif g >= 0.10:
            score += 1.0; hits.append("revenue_growth_moderate(+1)")
        elif g < 0:
            score -= 2.0; hits.append("revenue_declining(-2)")

    fm = ind.fcf_margin
    if fm is not None:
        if fm >= 0.20:
            score += 1.5; hits.append("fcf_strong(+1.5)")
        elif fm < 0:
            score -= 1.5; hits.append("fcf_negative(-1.5)")

    if ind.roe is not None:
        if ind.roe >= 0.20:
            score += 1.0; hits.append("roe_strong(+1)")
        elif ind.roe < 0.05:
            score -= 1.0; hits.append("roe_weak(-1)")

    nd = ind.net_debt_to_ebitda
    if nd is not None:
        if nd < 0:
            score += 0.5; hits.append("net_cash_position(+0.5)")
        elif nd > 3:
            score -= 1.0; hits.append("high_leverage(-1)")

    if ind.earnings_beat_streak >= 4:
        score += 0.5; hits.append("beat_streak(+0.5)")

    return DimensionScore(value=_clamp(score), hits=hits)


def score_valuation(ind: ValuationIndicators) -> DimensionScore:
    score = 5.0
    hits: list[str] = []

    pe = ind.pe_ttm
    if pe is not None:
        if pe < 0:
            score -= 1.0; hits.append("pe_negative(-1)")
        elif pe > 50:
            score -= 2.0; hits.append("pe_very_premium(-2)")
        elif pe > 30:
            score -= 1.0; hits.append("pe_premium(-1)")
        elif pe < 15:
            score += 1.0; hits.append("pe_cheap(+1)")

    ps = ind.ps
    if ps is not None:
        if ps > 20:
            score -= 1.5; hits.append("ps_extreme(-1.5)")
        elif ps < 3:
            score += 0.5; hits.append("ps_reasonable(+0.5)")

    up = ind.dcf_upside_pct
    if up is not None:
        if up >= 0.30:
            score += 2.5; hits.append("dcf_significant_upside(+2.5)")
        elif up >= 0.10:
            score += 1.0; hits.append("dcf_moderate_upside(+1)")
        elif up <= -0.20:
            score -= 1.5; hits.append("dcf_overvalued(-1.5)")

    return DimensionScore(value=_clamp(score), hits=hits)


def score_technicals(ind: TechnicalsIndicators) -> DimensionScore:
    score = 5.0
    hits: list[str] = []

    if ind.price_vs_sma200_pct is not None:
        if ind.price_vs_sma200_pct > 0:
            score += 1.5; hits.append("above_sma200(+1.5)")
        else:
            score -= 1.5; hits.append("below_sma200(-1.5)")

    if ind.golden_cross:
        score += 1.0; hits.append("golden_cross(+1)")
    if ind.death_cross:
        score -= 1.0; hits.append("death_cross(-1)")

    rsi = ind.rsi_14
    if rsi is not None:
        if 40 <= rsi <= 65:
            score += 1.0; hits.append("rsi_healthy(+1)")
        elif rsi > 75:
            score -= 1.0; hits.append("rsi_overbought(-1)")
        elif rsi < 30:
            score -= 0.5; hits.append("rsi_oversold(-0.5)")

    if ind.macd_signal == "positive":
        score += 0.5; hits.append("macd_positive(+0.5)")
    elif ind.macd_signal == "negative":
        score -= 0.5; hits.append("macd_negative(-0.5)")

    if ind.volume_20d_vs_60d_pct is not None and ind.volume_20d_vs_60d_pct > 0.05:
        score += 0.5; hits.append("volume_confirming(+0.5)")

    return DimensionScore(value=_clamp(score), hits=hits)


def score_sentiment(analyst: AnalystData, ownership: OwnershipData) -> DimensionScore:
    score = 5.0
    hits: list[str] = []

    total = analyst.num_buy + analyst.num_hold + analyst.num_sell
    if total > 0:
        buy_ratio = analyst.num_buy / total
        if buy_ratio >= 0.75:
            score += 2.0; hits.append("analyst_consensus_strong_buy(+2)")
        elif buy_ratio >= 0.50:
            score += 1.0; hits.append("analyst_consensus_buy(+1)")
        elif buy_ratio < 0.25:
            score -= 1.5; hits.append("analyst_consensus_bearish(-1.5)")

    if ownership.institutional_pct_change_qoq is not None:
        if ownership.institutional_pct_change_qoq > 0.01:
            score += 1.0; hits.append("institutional_buying(+1)")
        elif ownership.institutional_pct_change_qoq < -0.01:
            score -= 1.0; hits.append("institutional_selling(-1)")

    if ownership.insider_net_buying_90d is not None:
        if ownership.insider_net_buying_90d > 0:
            score += 1.5; hits.append("insider_buying(+1.5)")
        elif ownership.insider_net_buying_90d < -1e8:  # >$100M selling
            score -= 1.5; hits.append("insider_selling_large(-1.5)")

    return DimensionScore(value=_clamp(score), hits=hits)


def compose(
    indicators: Indicators,
    analyst: AnalystData,
    ownership: OwnershipData,
) -> CompositeScore:
    f = score_fundamentals(indicators.fundamentals)
    v = score_valuation(indicators.valuation)
    t = score_technicals(indicators.technicals)
    s = score_sentiment(analyst, ownership)

    weights = {
        "fundamentals": 0.30,
        "valuation": 0.30,
        "technicals": 0.20,
        "sentiment": 0.20,
    }
    composite = (
        f.value * weights["fundamentals"]
        + v.value * weights["valuation"]
        + t.value * weights["technicals"]
        + s.value * weights["sentiment"]
    )
    return CompositeScore(
        fundamentals=f, valuation=v, technicals=t, sentiment=s,
        weights=weights, composite=round(composite, 2),
    )
```

- [ ] **Step 5: Run, expect pass**

```bash
uv run pytest tests/test_scoring_rubric.py -v
```

Expected: 7 passed.

- [ ] **Step 6: Commit**

```bash
git add src/stock_analytics/scoring/__init__.py src/stock_analytics/scoring/rubric.py tests/test_scoring_rubric.py
git commit -m "feat(scoring): deterministic rubric for four dimensions plus weighted composite"
```

---

## Task 11: Red flags detector

**Files:**
- Create: `src/stock_analytics/scoring/red_flags.py`
- Create: `tests/test_red_flags.py`

Programmatic red flags that should NOT depend on LLM judgment.

- [ ] **Step 1: Write the failing tests**

`tests/test_red_flags.py`:
```python
import pytest

from stock_analytics.briefing.schema import (
    FundamentalsIndicators, Indicators, TechnicalsIndicators, ValuationIndicators,
)
from stock_analytics.scoring.red_flags import detect_red_flags


def test_detects_extreme_ps(sample_nvda_raw):
    indicators = Indicators(
        fundamentals=FundamentalsIndicators(),
        valuation=ValuationIndicators(ps=35.0),
        technicals=TechnicalsIndicators(),
    )
    flags = detect_red_flags(sample_nvda_raw, indicators)
    assert any(f.code == "ps_extreme" for f in flags)


def test_detects_negative_fcf(sample_nvda_raw):
    indicators = Indicators(
        fundamentals=FundamentalsIndicators(fcf_margin=-0.05),
        valuation=ValuationIndicators(),
        technicals=TechnicalsIndicators(),
    )
    flags = detect_red_flags(sample_nvda_raw, indicators)
    assert any(f.code == "negative_fcf" for f in flags)


def test_detects_insider_selling_acceleration(sample_nvda_raw):
    indicators = Indicators(
        fundamentals=FundamentalsIndicators(),
        valuation=ValuationIndicators(),
        technicals=TechnicalsIndicators(),
    )
    flags = detect_red_flags(sample_nvda_raw, indicators)
    # Sample NVDA fixture has -250M insider net buying
    assert any(f.code == "insider_selling_large" for f in flags)


def test_no_flags_for_healthy_company():
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from stock_analytics.briefing.schema import (
        AnalystData, CompanySnapshot, FundamentalsData, NewsData,
        OwnershipData, PriceData, RawData,
    )
    et = ZoneInfo("America/New_York")
    now = datetime.now(et)
    raw = RawData(
        snapshot=CompanySnapshot(ticker="X", name="X", current_price=100.0),
        price=PriceData(history=[], source="t", fetched_at=now),
        fundamentals=FundamentalsData(source="t", fetched_at=now),
        ownership=OwnershipData(
            insider_net_buying_90d=10_000_000, source="t", fetched_at=now,
        ),
        analyst=AnalystData(source="t", fetched_at=now),
        news=NewsData(items=[], source="t", fetched_at=now),
        as_of=now,
    )
    indicators = Indicators(
        fundamentals=FundamentalsIndicators(fcf_margin=0.20),
        valuation=ValuationIndicators(ps=5.0),
        technicals=TechnicalsIndicators(),
    )
    flags = detect_red_flags(raw, indicators)
    assert all(f.severity != "critical" for f in flags)
```

- [ ] **Step 2: Run, expect failure**

```bash
uv run pytest tests/test_red_flags.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `red_flags.py`**

`src/stock_analytics/scoring/red_flags.py`:
```python
"""Programmatic red flag detection. Run on every briefing."""
from stock_analytics.briefing.schema import Indicators, RawData, RedFlag


def detect_red_flags(raw: RawData, indicators: Indicators) -> list[RedFlag]:
    flags: list[RedFlag] = []

    # Valuation red flags
    if indicators.valuation.ps is not None and indicators.valuation.ps > 25:
        flags.append(RedFlag(
            severity="warn",
            code="ps_extreme",
            message=f"P/S ratio {indicators.valuation.ps:.1f} is extreme; historically associated with subsequent multiple compression.",
        ))

    if indicators.valuation.pe_ttm is not None and indicators.valuation.pe_ttm < 0:
        flags.append(RedFlag(
            severity="warn",
            code="unprofitable",
            message="Company is unprofitable on TTM basis (negative P/E).",
        ))

    # Fundamentals red flags
    if indicators.fundamentals.fcf_margin is not None and indicators.fundamentals.fcf_margin < 0:
        flags.append(RedFlag(
            severity="warn",
            code="negative_fcf",
            message="Free cash flow margin is negative — company is burning cash.",
        ))

    if indicators.fundamentals.net_debt_to_ebitda is not None and indicators.fundamentals.net_debt_to_ebitda > 4:
        flags.append(RedFlag(
            severity="warn",
            code="high_leverage",
            message=f"Net debt / EBITDA at {indicators.fundamentals.net_debt_to_ebitda:.1f} indicates high leverage.",
        ))

    if indicators.fundamentals.revenue_growth_yoy is not None and indicators.fundamentals.revenue_growth_yoy < -0.10:
        flags.append(RedFlag(
            severity="critical",
            code="revenue_collapse",
            message=f"Revenue down {indicators.fundamentals.revenue_growth_yoy * 100:.1f}% YoY.",
        ))

    # Ownership red flags
    if raw.ownership.insider_net_buying_90d is not None and raw.ownership.insider_net_buying_90d < -1e8:
        flags.append(RedFlag(
            severity="warn",
            code="insider_selling_large",
            message=f"Insiders sold ${abs(raw.ownership.insider_net_buying_90d) / 1e6:.0f}M (net) in last 90 days.",
        ))

    return flags
```

- [ ] **Step 4: Run, expect pass**

```bash
uv run pytest tests/test_red_flags.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/stock_analytics/scoring/red_flags.py tests/test_red_flags.py
git commit -m "feat(scoring): programmatic red flag detection"
```

---

## Task 12: Briefing builder

**Files:**
- Create: `src/stock_analytics/briefing/builder.py`
- Create: `tests/test_briefing_builder.py`

Converts a `ScoredBriefing` into the markdown defined in spec §6. This is the document Claude reads.

- [ ] **Step 1: Write the failing tests**

`tests/test_briefing_builder.py`:
```python
import pytest

from stock_analytics.briefing.builder import build_briefing_markdown
from stock_analytics.briefing.schema import (
    CompositeScore, DimensionScore, FundamentalsIndicators, Indicators,
    ScoredBriefing, TechnicalsIndicators, ValuationIndicators,
)
from stock_analytics.scoring.red_flags import detect_red_flags


def _make_scored(raw):
    indicators = Indicators(
        fundamentals=FundamentalsIndicators(
            revenue_growth_yoy=0.667, fcf_margin=0.475, roe=1.0,
            net_debt_to_ebitda=-0.31, earnings_beat_streak=4,
        ),
        valuation=ValuationIndicators(
            pe_ttm=60.0, ps=30.0, ev_ebitda=45.85, pb=60.0,
            dcf_fair_value=850.0, dcf_upside_pct=-0.056,
            dcf_assumptions={"wacc": 0.09, "terminal_growth": 0.03, "growth_path": [0.25, 0.20, 0.16, 0.12, 0.08]},
        ),
        technicals=TechnicalsIndicators(
            sma_50=880.0, sma_200=750.0, price_vs_sma200_pct=0.20,
            golden_cross=True, rsi_14=58, macd_signal="positive",
        ),
    )
    scores = CompositeScore(
        fundamentals=DimensionScore(value=8.5, hits=["revenue_growth_high(+2)"]),
        valuation=DimensionScore(value=4.5, hits=["ps_extreme(-1.5)"]),
        technicals=DimensionScore(value=7.5, hits=["above_sma200(+1.5)"]),
        sentiment=DimensionScore(value=6.0, hits=["analyst_consensus_buy(+1)"]),
        composite=6.6,
    )
    return ScoredBriefing(
        raw=raw, indicators=indicators, scores=scores,
        red_flags=detect_red_flags(raw, indicators), as_of=raw.as_of,
    )


def test_briefing_contains_timeguard(sample_nvda_raw):
    md = build_briefing_markdown(_make_scored(sample_nvda_raw))
    assert "TIMEGUARD" in md
    assert "2026-04-09" in md


def test_briefing_has_all_sections(sample_nvda_raw):
    md = build_briefing_markdown(_make_scored(sample_nvda_raw))
    for header in [
        "## 0 · Snapshot",
        "## 1 · Fundamentals",
        "## 2 · Valuation",
        "## 3 · Technicals",
        "## 4 · Sentiment & Flow",
        "## 5 · Aggregate",
        "## 6 · Red Flags",
        "## 7 · Data Provenance",
    ]:
        assert header in md, f"Missing section: {header}"


def test_briefing_includes_scores(sample_nvda_raw):
    md = build_briefing_markdown(_make_scored(sample_nvda_raw))
    assert "8.5" in md  # fundamentals score
    assert "Composite" in md
    assert "6.6" in md


def test_briefing_includes_rubric_hits(sample_nvda_raw):
    md = build_briefing_markdown(_make_scored(sample_nvda_raw))
    assert "revenue_growth_high(+2)" in md
    assert "ps_extreme(-1.5)" in md


def test_briefing_includes_dcf_assumptions(sample_nvda_raw):
    md = build_briefing_markdown(_make_scored(sample_nvda_raw))
    assert "WACC" in md or "wacc" in md
    assert "0.09" in md or "9" in md
```

- [ ] **Step 2: Run, expect failure**

```bash
uv run pytest tests/test_briefing_builder.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `builder.py`**

`src/stock_analytics/briefing/builder.py`:
```python
"""ScoredBriefing → markdown. The output is the only thing Claude sees."""
from stock_analytics.briefing.schema import ScoredBriefing
from stock_analytics.utils.timeguard import format_as_of


def _fmt_pct(x: float | None) -> str:
    return f"{x * 100:+.1f}%" if x is not None else "n/a"


def _fmt_num(x: float | None, decimals: int = 2) -> str:
    return f"{x:.{decimals}f}" if x is not None else "n/a"


def _fmt_money(x: float | None) -> str:
    if x is None:
        return "n/a"
    if abs(x) >= 1e12:
        return f"${x / 1e12:.2f}T"
    if abs(x) >= 1e9:
        return f"${x / 1e9:.2f}B"
    if abs(x) >= 1e6:
        return f"${x / 1e6:.1f}M"
    return f"${x:,.0f}"


def build_briefing_markdown(sb: ScoredBriefing) -> str:
    s = sb.raw.snapshot
    f = sb.raw.fundamentals
    fi = sb.indicators.fundamentals
    vi = sb.indicators.valuation
    ti = sb.indicators.technicals
    sc = sb.scores
    as_of_str = format_as_of(sb.as_of)

    parts: list[str] = []
    parts.append(f"# {s.ticker} Briefing · as_of: {as_of_str}\n")
    parts.append(f"> ⚠️ TIMEGUARD: All data through {as_of_str}. Do not reference events after this date.\n")

    # 0 Snapshot
    parts.append("## 0 · Snapshot\n")
    parts.append(f"- Company: {s.name}")
    parts.append(f"- Sector / Industry: {s.sector or 'n/a'} / {s.industry or 'n/a'}")
    parts.append(f"- Market Cap: {_fmt_money(s.market_cap)}")
    parts.append(f"- Price: ${s.current_price:.2f}  (52W: ${s.week52_low or 0:.2f} – ${s.week52_high or 0:.2f})")
    parts.append(f"- Avg Volume (20d): {_fmt_num(s.avg_volume_20d, 0) if s.avg_volume_20d else 'n/a'}\n")

    # 1 Fundamentals
    parts.append("## 1 · Fundamentals\n")
    parts.append("### Raw\n")
    parts.append("| Metric | Value |")
    parts.append("|---|---|")
    parts.append(f"| Revenue (TTM) | {_fmt_money(f.revenue_ttm)} |")
    parts.append(f"| Revenue YoY | {_fmt_pct(fi.revenue_growth_yoy)} |")
    parts.append(f"| Revenue 3Y CAGR | {_fmt_pct(fi.revenue_cagr_3y)} |")
    parts.append(f"| Gross Margin | {_fmt_pct(fi.gross_margin)} |")
    parts.append(f"| Operating Margin | {_fmt_pct(fi.operating_margin)} |")
    parts.append(f"| Net Margin | {_fmt_pct(fi.net_margin)} |")
    parts.append(f"| FCF Margin | {_fmt_pct(fi.fcf_margin)} |")
    parts.append(f"| FCF / Net Income | {_fmt_pct(fi.fcf_to_net_income)} |")
    parts.append(f"| ROE | {_fmt_pct(fi.roe)} |")
    parts.append(f"| Net Debt / EBITDA | {_fmt_num(fi.net_debt_to_ebitda)} |")
    parts.append(f"| Earnings beat streak | {fi.earnings_beat_streak} |\n")
    parts.append(f"### Score: {sc.fundamentals.value:.1f} / 10")
    parts.append(f"**Rubric hits**: {', '.join(sc.fundamentals.hits) or 'none'}\n")

    # 2 Valuation
    parts.append("## 2 · Valuation\n")
    parts.append("### Multiples\n")
    parts.append("| Metric | Value | Industry Median |")
    parts.append("|---|---|---|")
    parts.append(f"| P/E (TTM) | {_fmt_num(vi.pe_ttm)} | {_fmt_num(vi.industry_pe_median)} |")
    parts.append(f"| EV/EBITDA | {_fmt_num(vi.ev_ebitda)} | {_fmt_num(vi.industry_ev_ebitda_median)} |")
    parts.append(f"| P/S | {_fmt_num(vi.ps)} | — |")
    parts.append(f"| P/B | {_fmt_num(vi.pb)} | — |\n")
    parts.append("### Simple DCF (transparent assumptions)\n")
    parts.append(f"- WACC: {vi.dcf_assumptions.get('wacc', 'n/a')}")
    parts.append(f"- Terminal growth: {vi.dcf_assumptions.get('terminal_growth', 'n/a')}")
    parts.append(f"- 5Y growth path: {vi.dcf_assumptions.get('growth_path', 'n/a')}")
    parts.append(f"- **Implied fair value: ${_fmt_num(vi.dcf_fair_value)}** (vs current ${s.current_price:.2f} → {_fmt_pct(vi.dcf_upside_pct)})\n")
    parts.append(f"### Score: {sc.valuation.value:.1f} / 10")
    parts.append(f"**Rubric hits**: {', '.join(sc.valuation.hits) or 'none'}\n")

    # 3 Technicals
    parts.append("## 3 · Technicals\n")
    parts.append(f"- Price vs SMA50: {_fmt_pct(ti.price_vs_sma50_pct)}")
    parts.append(f"- Price vs SMA200: {_fmt_pct(ti.price_vs_sma200_pct)}")
    parts.append(f"- Golden cross: {ti.golden_cross}  ·  Death cross: {ti.death_cross}")
    parts.append(f"- RSI(14): {_fmt_num(ti.rsi_14, 1)}")
    parts.append(f"- MACD signal: {ti.macd_signal}")
    parts.append(f"- Volume 20d vs 60d: {_fmt_pct(ti.volume_20d_vs_60d_pct)}")
    parts.append(f"- Distance from 52W high: {_fmt_pct(ti.distance_from_52w_high_pct)}\n")
    parts.append(f"### Score: {sc.technicals.value:.1f} / 10")
    parts.append(f"**Rubric hits**: {', '.join(sc.technicals.hits) or 'none'}\n")

    # 4 Sentiment & Flow
    a = sb.raw.analyst
    o = sb.raw.ownership
    parts.append("## 4 · Sentiment & Flow\n")
    parts.append(f"- Analyst consensus: {a.consensus or 'n/a'} ({a.num_buy} buy / {a.num_hold} hold / {a.num_sell} sell)")
    parts.append(f"- Avg target: {_fmt_num(a.target_mean)} (range {_fmt_num(a.target_low)} – {_fmt_num(a.target_high)})")
    parts.append(f"- Institutional Δ QoQ: {_fmt_pct(o.institutional_pct_change_qoq)}")
    parts.append(f"- Insider net buying (90d): {_fmt_money(o.insider_net_buying_90d)}\n")
    if sb.raw.news.items:
        parts.append("**Recent news (top 5):**")
        for item in sb.raw.news.items[:5]:
            parts.append(f"- [{item.date.strftime('%Y-%m-%d')}] {item.headline} — {item.sentiment}")
        parts.append("")
    parts.append(f"### Score: {sc.sentiment.value:.1f} / 10")
    parts.append(f"**Rubric hits**: {', '.join(sc.sentiment.hits) or 'none'}\n")

    # 5 Aggregate
    parts.append("## 5 · Aggregate\n")
    for dim in ("fundamentals", "valuation", "technicals", "sentiment"):
        score = getattr(sc, dim).value
        weight = sc.weights[dim]
        parts.append(f"- {dim.capitalize():<13} {score:.2f} × {weight:.2f} = {score * weight:.2f}")
    parts.append(f"- **Composite: {sc.composite:.2f} / 10**\n")

    # 6 Red Flags
    parts.append("## 6 · Red Flags (auto-detected)\n")
    if sb.red_flags:
        for rf in sb.red_flags:
            icon = {"info": "ℹ️", "warn": "⚠️", "critical": "🛑"}[rf.severity]
            parts.append(f"- {icon} **{rf.code}**: {rf.message}")
    else:
        parts.append("- ✅ No red flags detected.")
    parts.append("")

    # 7 Provenance
    parts.append("## 7 · Data Provenance\n")
    parts.append(f"- price: {sb.raw.price.source}, fetched {sb.raw.price.fetched_at}")
    parts.append(f"- fundamentals: {sb.raw.fundamentals.source}, fetched {sb.raw.fundamentals.fetched_at}")
    parts.append(f"- ownership: {sb.raw.ownership.source}, fetched {sb.raw.ownership.fetched_at}")
    parts.append(f"- analyst: {sb.raw.analyst.source}, fetched {sb.raw.analyst.fetched_at}")
    parts.append(f"- news: {sb.raw.news.source}, fetched {sb.raw.news.fetched_at}")

    return "\n".join(parts)
```

- [ ] **Step 4: Run, expect pass**

```bash
uv run pytest tests/test_briefing_builder.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add src/stock_analytics/briefing/builder.py tests/test_briefing_builder.py
git commit -m "feat(briefing): markdown builder per spec section 6"
```

---

## Task 13: Price fetcher

**Files:**
- Create: `src/stock_analytics/fetchers/__init__.py`
- Create: `src/stock_analytics/fetchers/price.py`

Fetchers do **not** get unit tests. They are validated by the smoke script in Task 18.

- [ ] **Step 1: Create empty `__init__.py`**

`src/stock_analytics/fetchers/__init__.py`: empty.

- [ ] **Step 2: Implement `price.py`**

`src/stock_analytics/fetchers/price.py`:
```python
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
```

- [ ] **Step 3: Quick smoke check (manual; ok if it errors with rate-limit, that's the API)**

```bash
uv run python -c "
from datetime import datetime
from stock_analytics.fetchers.price import fetch_price_and_snapshot
from stock_analytics.utils.timeguard import now_et
snap, price = fetch_price_and_snapshot('AAPL', now_et())
print(snap.name, snap.current_price, len(price.history), 'bars')
"
```

Expected: something like `Apple Inc. 175.43 502 bars`. If yfinance is rate-limited, retry in a minute.

- [ ] **Step 4: Commit**

```bash
git add src/stock_analytics/fetchers/__init__.py src/stock_analytics/fetchers/price.py
git commit -m "feat(fetchers): price + snapshot via yfinance"
```

---

## Task 14: Fundamentals fetcher

**Files:**
- Create: `src/stock_analytics/fetchers/fundamentals.py`

- [ ] **Step 1: Implement `fundamentals.py`**

`src/stock_analytics/fetchers/fundamentals.py`:
```python
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
        book_value=_get(bs, "Stockholders Equity", 0) or info.get("bookValue", 0) * (info.get("sharesOutstanding") or 0) or None,
        earnings_beat_streak=0,  # yfinance doesn't expose this cleanly; v1 leaves 0
        source="yfinance",
        fetched_at=fetched_at,
    )
```

- [ ] **Step 2: Smoke check**

```bash
uv run python -c "
from stock_analytics.fetchers.fundamentals import fetch_fundamentals
from stock_analytics.utils.timeguard import now_et
f = fetch_fundamentals('AAPL', now_et())
print('Rev TTM:', f.revenue_ttm)
print('Net income TTM:', f.net_income_ttm)
print('FCF TTM:', f.free_cash_flow_ttm)
"
```

Expected: positive numbers for each. If anything is None, that's noted in briefing as "data not provided".

- [ ] **Step 3: Commit**

```bash
git add src/stock_analytics/fetchers/fundamentals.py
git commit -m "feat(fetchers): fundamentals via yfinance with TTM aggregation"
```

---

## Task 15: Ownership, analyst, and news fetchers

**Files:**
- Create: `src/stock_analytics/fetchers/ownership.py`
- Create: `src/stock_analytics/fetchers/analyst.py`
- Create: `src/stock_analytics/fetchers/news.py`

Three small fetchers grouped because each is straightforward.

- [ ] **Step 1: Implement `ownership.py`**

`src/stock_analytics/fetchers/ownership.py`:
```python
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
```

- [ ] **Step 2: Implement `analyst.py`**

`src/stock_analytics/fetchers/analyst.py`:
```python
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

    consensus = info.get("recommendationKey", "").upper() or None
    if consensus == "STRONG_BUY":
        consensus = "BUY"

    return AnalystData(
        consensus=consensus,
        target_mean=info.get("targetMeanPrice"),
        target_high=info.get("targetHighPrice"),
        target_low=info.get("targetLowPrice"),
        num_buy=info.get("numberOfAnalystOpinions", 0) if consensus == "BUY" else 0,
        num_hold=0,
        num_sell=0,
        recent_revisions=revisions[-5:],
        source="yfinance",
        fetched_at=fetched_at,
    )
```

- [ ] **Step 3: Implement `news.py`**

`src/stock_analytics/fetchers/news.py`:
```python
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
```

- [ ] **Step 4: Smoke check all three**

```bash
uv run python -c "
from stock_analytics.fetchers.ownership import fetch_ownership
from stock_analytics.fetchers.analyst import fetch_analyst
from stock_analytics.fetchers.news import fetch_news
from stock_analytics.utils.timeguard import now_et
n = now_et()
o = fetch_ownership('AAPL', n)
a = fetch_analyst('AAPL', n)
nw = fetch_news('AAPL', n)
print('inst%:', o.institutional_pct)
print('analyst target:', a.target_mean)
print('news count:', len(nw.items))
"
```

Expected: institutional % ~0.6, target a positive number, several news items.

- [ ] **Step 5: Commit**

```bash
git add src/stock_analytics/fetchers/ownership.py src/stock_analytics/fetchers/analyst.py src/stock_analytics/fetchers/news.py
git commit -m "feat(fetchers): ownership, analyst, and news via yfinance"
```

---

## Task 16: CLI orchestration

**Files:**
- Modify: `src/stock_analytics/cli.py`

The CLI ties everything together: parse ticker, fetch (or read cache), compute, score, build briefing, write outputs.

- [ ] **Step 1: Replace stub `cli.py`**

`src/stock_analytics/cli.py`:
```python
"""CLI entry point. One run = one ticker analysis."""
from __future__ import annotations

import argparse
import json
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
```

- [ ] **Step 2: Run end-to-end**

```bash
uv run python -m stock_analytics AAPL
```

Expected:
- Console shows "Fetching AAPL..." then "✓ Briefing: ..." with a path
- File `data/AAPL_2026-04-09.json` exists
- File `data/AAPL_2026-04-09_briefing.md` exists and contains all 8 sections from spec §6
- Composite score is a number 0–10

- [ ] **Step 3: Inspect the briefing**

```bash
cat data/AAPL_$(date +%Y-%m-%d)_briefing.md | head -60
```

Verify it has sections 0–7 and rubric hits look reasonable.

- [ ] **Step 4: Run again to verify cache hit**

```bash
uv run python -m stock_analytics AAPL
```

Expected: "Cache hit for AAPL" message; no API calls.

- [ ] **Step 5: Commit**

```bash
git add src/stock_analytics/cli.py
git commit -m "feat(cli): orchestrate fetch → indicators → scoring → briefing"
```

---

## Task 17: Prompts (rules + short + full templates)

**Files:**
- Create: `prompts/rules.md`
- Create: `prompts/analyst_short.md`
- Create: `prompts/analyst_full.md`

These are the instructions Claude reads when producing reports.

- [ ] **Step 1: Create `prompts/rules.md`**

```markdown
# Analyst Rules (read this first, every time)

You are analyzing data exclusively from the briefing.md file you were just shown. Follow these rules without exception.

## 1. NO NUMBER GENERATION

Every number in your report must appear verbatim in the briefing. Do not estimate, infer, recall, or compute. If a number is missing from the briefing, write "data not provided" — never substitute a guess.

## 2. CITE EVERY CLAIM

Each claim must reference a specific metric from the briefing.

❌ "Revenue growth is good"
✅ "Revenue growth is strong (TTM +66.7% YoY, see briefing §1)"

## 3. BOTH SIDES MANDATORY

You must produce **at least 3 bull arguments AND at least 3 bear arguments**. If you cannot find ≥3 of one side, explicitly write:

> "Counter-arguments insufficient — this asymmetry is itself a risk signal worth flagging."

## 4. LEAN + CONFIDENCE + HUMILITY

End every report with this exact structure:

```
**Lean:** {strong buy / lean bull / neutral / lean bear / strong sell}
**Confidence:** {1–10}
**Three reasons I might be wrong:**
1. ...
2. ...
3. ...
```

## 5. QUESTIONS FOR THE USER

List 3–5 questions whose answers would change the conclusion. These force the user to think, not just consume.

## 6. NOT AN ADVISOR

Never say "I recommend you buy/sell". You are an analyst. The decision belongs to the user.

## 7. TIMEGUARD

The briefing's `as_of` date is your knowledge cutoff for this analysis. Do not reference events, prices, or news after that date — even if you remember them.

## 8. RED FLAGS ARE LOAD-BEARING

If the briefing's §6 (Red Flags) contains any items, you must address each one explicitly in your report. Don't bury them.
```

- [ ] **Step 2: Create `prompts/analyst_short.md`**

```markdown
# Short Report Template (Telegram-friendly, ≤ 4096 chars)

You have just read the briefing for a US stock. Produce a SHORT report following this exact format. Aim for ≤ 4000 characters.

```
📊 {TICKER} · {as_of date} · ${current price}

🟢/🟡/🔴 Fundamentals  {score}/10  {one-line rationale citing top hit}
🟢/🟡/🔴 Valuation     {score}/10  {one-line rationale}
🟢/🟡/🔴 Technicals    {score}/10  {one-line rationale}
🟢/🟡/🔴 Sentiment     {score}/10  {one-line rationale}

🎯 Composite: {composite}/10 — {Lean text}

✅ Top 3 bull points:
• {point 1, with metric citation}
• {point 2}
• {point 3}

⚠️ Top 3 bear points:
• {point 1, with metric citation}
• {point 2}
• {point 3}

🚩 Red flags: {list any from briefing §6, or "none detected"}

❓ Ask yourself:
• {question 1}
• {question 2}
• {question 3}

📌 Lean: {strong buy / lean bull / neutral / lean bear / strong sell}
📌 Confidence: {1–10}
📌 I might be wrong because: {one sentence}
```

Color rules: 🟢 ≥7, 🟡 4–6.9, 🔴 <4

Strict rules from `prompts/rules.md` apply. Especially: no fabricated numbers, both sides required, never give an "I recommend" statement.
```

- [ ] **Step 3: Create `prompts/analyst_full.md`**

```markdown
# Full Report Template (1500–3000 words, deep dive)

You have just read the briefing for a US stock. Produce a LONG report. Follow `prompts/rules.md` strictly.

## Required sections

### Executive Summary (≤ 150 words)
Composite score, lean, confidence, the single most important fact about this name today.

### 1. Fundamentals Deep Dive (300–500 words)
- Walk through the rubric hits from briefing §1
- Address growth quality, profitability, balance sheet, cash generation
- Quantify everything with metrics from the briefing
- Flag any data marked "not provided" — this affects how confident the analysis can be

### 2. Valuation Deep Dive (300–500 words)
- Multiples in context: vs industry median (if available), vs own history (if mentioned)
- Walk through the DCF: state the assumptions explicitly, then critique whether they're reasonable for this name
- Be honest if the DCF assumptions don't fit the company (e.g., high-growth disruptor doesn't fit a fade-to-8% model)

### 3. Technicals Read (200–400 words)
- Trend, momentum, volume confirmation
- Distance from 52W high — what does it mean here
- Be modest: technicals are short-term hints, not edge

### 4. Sentiment & Flow (200–400 words)
- Analyst consensus and what it might miss
- Insider/institutional flow — interpret direction and size
- Recent news (if any in briefing) — note signal vs noise

### 5. Bull Case (≥3 points, each with metric citation)

### 6. Bear Case (≥3 points, each with metric citation)
If you struggle to find 3, write the asymmetry warning per rules.md §3.

### 7. Red Flags Discussion
Address every item from briefing §6 individually.

### 8. Questions for the User (3–5)
Questions whose answers would change the conclusion.

### 9. Final Lean
```
**Lean:** {...}
**Confidence:** {1–10}
**Three reasons I might be wrong:**
1. ...
2. ...
3. ...
```

### 10. What I Did Not Analyze
List things a human should still check: macro context, supply chain, management quality, competitive moat in qualitative terms, regulatory exposure. The briefing only contains numbers.
```

- [ ] **Step 4: Commit**

```bash
git add prompts/
git commit -m "feat(prompts): rules + short and full report templates"
```

---

## Task 18: Smoke test script

**Files:**
- Create: `scripts/smoke_test.py`

A manual script that exercises every fetcher and the full pipeline against a real ticker. Run before any release / after dependency upgrades.

- [ ] **Step 1: Create `scripts/smoke_test.py`**

```python
"""Manual smoke test. Hits live APIs. Run after dependency changes."""
from __future__ import annotations

import sys

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
            console.print(f"[green]✓[/green] {t}: price={snap.current_price:.2f} bars={len(price.history)} "
                          f"rev_ttm={fund.revenue_ttm} inst%={own.institutional_pct} "
                          f"target={an.target_mean} news={len(news.items)}")
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
```

- [ ] **Step 2: Run smoke test**

```bash
uv run python scripts/smoke_test.py
```

Expected: All three tickers ✓ on both fetcher and pipeline runs. Some fields may be `None` for BRK-B (it's structured oddly); that's acceptable.

- [ ] **Step 3: Inspect generated briefings**

```bash
ls data/*_briefing.md
```

Expected: at least 3 briefing files. Open one and verify all 8 sections are present.

- [ ] **Step 4: Commit**

```bash
git add scripts/smoke_test.py
git commit -m "test: add manual smoke script for fetchers and full pipeline"
```

---

## Task 19: Slash command + reports index

**Files:**
- Create: `.claude/commands/analyze.md`
- Create: `reports/_index.csv` (header only)

This is the user-facing piece. Once installed, `/analyze NVDA` in Claude Code triggers the full flow.

- [ ] **Step 1: Create the slash command**

`.claude/commands/analyze.md`:
```markdown
---
description: Analyze a US stock ticker — Python computes data, you produce short and long reports
argument-hint: <TICKER>
---

You are about to analyze the US stock $ARGUMENTS. Follow these steps in order:

## Step 1: Generate the briefing

Run this command:

```bash
cd /Users/anguslin/Documents/Claude_Agents/Stock_Analytics && uv run python -m stock_analytics $ARGUMENTS
```

Confirm the command output shows a briefing path.

## Step 2: Read the briefing and rules

Read these files in order:
1. `/Users/anguslin/Documents/Claude_Agents/Stock_Analytics/prompts/rules.md`
2. `/Users/anguslin/Documents/Claude_Agents/Stock_Analytics/prompts/analyst_short.md`
3. `/Users/anguslin/Documents/Claude_Agents/Stock_Analytics/prompts/analyst_full.md`
4. `/Users/anguslin/Documents/Claude_Agents/Stock_Analytics/data/$ARGUMENTS_<today>_briefing.md`

(Use the actual date from the previous step's output.)

## Step 3: Produce the SHORT report

Strictly following `rules.md` and `analyst_short.md`, produce the short report. Display it INLINE in this conversation.

## Step 4: Produce the LONG report

Strictly following `rules.md` and `analyst_full.md`, produce the long report. Save it to:
`/Users/anguslin/Documents/Claude_Agents/Stock_Analytics/reports/$ARGUMENTS_<today>_full.md`

## Step 5: Update the index

Append one line to `/Users/anguslin/Documents/Claude_Agents/Stock_Analytics/reports/_index.csv`:
`<date>,<ticker>,<composite_score>,<lean>`

## Step 6: Closing message

End your response with:
- The path to the long report
- "Ask follow-up questions about any dimension — I'll use the same briefing without re-fetching."

## Hard rules (from rules.md, do not violate)
- No fabricated numbers
- Both bull AND bear arguments mandatory (≥3 each)
- Lean + confidence + "three reasons I might be wrong"
- Never say "I recommend you buy/sell"
- Honor TIMEGUARD: don't reference events after the briefing's as_of date
```

- [ ] **Step 2: Create reports index**

```bash
mkdir -p reports
printf "date,ticker,composite,lean\n" > reports/_index.csv
```

- [ ] **Step 3: Verify slash command discoverable**

The slash command lives in the project's `.claude/commands/` so it's only available when Claude Code is invoked with this directory in its working set. Open Claude Code in this project root and verify `/analyze` appears in the slash command list.

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/analyze.md reports/_index.csv
git commit -m "feat: add /analyze slash command and reports index"
```

---

## Task 20: README and end-to-end real-run validation

**Files:**
- Modify: `README.md`

Final task: update README with usage, run one real analysis end-to-end with the slash command, and verify the success criteria from spec §15.

- [ ] **Step 1: Update README with full usage**

`README.md`:
```markdown
# Stock Analytics

Personal US-equity analysis tool. **Python computes the numbers, Claude Code narrates, you decide.**

Inspired by `virattt/ai-hedge-fund` but deliberately simpler: no agent persona role-play, no LLM-generated numbers, no auto buy/sell signals. The tool produces a structured briefing and Claude turns it into a report you can interrogate.

See `docs/specs/2026-04-09-stock-analytics-design.md` for the full design rationale.

## Setup

```bash
git clone <this repo>
cd Stock_Analytics
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

Produces `data/NVDA_<today>.json` and `data/NVDA_<today>_briefing.md`. No analysis report (that's Claude's job).

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
```

- [ ] **Step 2: Run full pytest suite**

```bash
uv run pytest
```

Expected: all tests pass.

- [ ] **Step 3: Run end-to-end smoke**

```bash
uv run python scripts/smoke_test.py
```

Expected: all three tickers ✓.

- [ ] **Step 4: Real-world validation via slash command**

In Claude Code, run `/analyze NVDA` (or another liquid US name). Verify:

- Short report appears inline with all required sections (scores, bull/bear, lean, confidence, questions)
- Long report file exists at `reports/NVDA_<today>_full.md`
- `reports/_index.csv` has a new row
- The report cites only numbers that appear in the briefing (spot-check 5 numbers)
- Both bull and bear arguments are present (≥3 each)
- "Three reasons I might be wrong" is included

If any of the above fails, iterate on the prompt files (`prompts/rules.md`, `analyst_short.md`, `analyst_full.md`) — no Python changes needed.

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: full README with usage and design summary"
```

---

## Self-Review (already completed inline)

**Spec coverage check:**

| Spec section | Implemented in |
|---|---|
| §2 Core Philosophy | Architecture; enforced by separation of layers |
| §3 Inspiration & Divergence | README + spec; no implementation needed |
| §4 Architecture | Tasks 1, 16, 19 |
| §5 Module Structure | Tasks 1–15 (all modules created) |
| §6 Briefing Structure | Task 12 (briefing builder) |
| §7 Prompt Rules | Task 17 |
| §8 Scoring Rubric | Task 10 |
| §9 Error Handling | CLI exception handling (Task 16); null-safety in indicators (Task 6) |
| §10 Testing Strategy | Tasks 3, 4, 6, 7, 8, 10, 11, 12, 18 |
| §11 Slash Command | Task 19 |
| §12 Dependencies | Task 1 (pyproject.toml) |
| §13 Open Question Decisions | DCF defaults in Task 7; reports/_index.csv in Task 19; single-ticker scope in Task 16 |
| §14 Out of Scope | Honored throughout (no multi-ticker, no backtester, no real-time) |
| §15 Success Criteria | Validated in Task 20 step 4 |

**Placeholder scan:** No TBDs, no "implement later", every code step has complete code.

**Type consistency:** All Pydantic models defined in Task 2 are referenced consistently. Function signatures match between definition and usage tasks.

---

## Notes for the implementer

- **TDD discipline matters here.** The indicator math is the foundation; if it's wrong, every layer above is wrong. Don't skip the "verify the test fails" step.
- **Fetcher fragility is expected.** yfinance changes its DataFrame schemas occasionally. If a smoke test fails after a yfinance upgrade, the fix is usually a column rename in `fetchers/fundamentals.py`.
- **The DCF is intentionally crude.** It's a sanity check, not a forecast. Don't make it more sophisticated without changing the spec — the whole point is that the assumptions are simple and visible.
- **Don't add unit tests for fetchers.** Mocks of yfinance go stale faster than the code they're testing. The smoke script is the right level.
- **Prompt iteration is part of the work.** After Task 20 step 4, expect to spend time tuning `prompts/*.md` based on actual Claude outputs. That's not "polish" — that's the core deliverable.
