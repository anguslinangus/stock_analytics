# Stock Analytics — Design Spec

- **Date:** 2026-04-09
- **Author:** angus + Claude
- **Status:** Approved, ready for implementation plan
- **Project root:** `/Users/anguslin/Documents/Claude_Agents/Stock_Analytics`

---

## 1. Goal

Build a personal stock analysis tool for **US equities** that helps the user evaluate whether to invest in a specific ticker. The tool produces structured, data-grounded analysis reports that act as a **rigorous second opinion**, not a buy/sell recommendation.

**Primary use case:** User types `/analyze NVDA` in Claude Code, receives a short report inline plus a long report saved to disk, and can follow up with conversational questions. Remote access via Claude cowork enables on-the-go usage (e.g., copy report to Telegram manually).

**Non-goals:**
- Real trading or order generation
- Backtesting strategies
- Portfolio optimization
- Multi-ticker comparison (deferred to v2)
- Auto-pushing to Telegram bot (cowork covers this need)

---

## 2. Core Philosophy

> **Python computes the numbers. Claude tells the story. The user makes the decision.**

Three layers of responsibility, strictly separated:

| Layer | Responsibility | Forbidden |
|---|---|---|
| Python data engine | Fetch data, compute indicators, score, build briefing | No LLM calls, no narrative |
| Claude Code (analyst) | Read briefing, write analysis using prompt template | No number generation, no fabrication |
| User | Final investment decision, follow-up questions | — |

**Key design principle:** Failures should be loud. Missing data must be explicit, never silently filled.

---

## 3. Inspiration & Divergence

Inspired by `virattt/ai-hedge-fund`'s multi-dimensional analyst decomposition and two-stage (analyst → synthesizer) flow. Deliberate divergences:

| ai-hedge-fund | This project | Why |
|---|---|---|
| 13 investor-persona agents | None | Persona ≠ alpha; LLM role-play is noise for real-money decisions |
| LangGraph / multi-agent orchestration | Plain Python + Claude Code | Claude Code IS the orchestrator |
| LLM call per agent | Python computes; one Claude pass | Save tokens, reproducible, prevents number fabrication |
| Built-in backtester | None | Not the goal; LLM backtests have severe look-ahead bias |
| Auto buy/sell signal | "Lean + confidence + counter-arguments required" | User decides; tool informs |
| Financial Datasets API primary | yfinance primary, FD secondary | Cost; yfinance covers ~80% for US equities |

---

## 4. Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Layer 3 · User                                          │
│  Final decisions, follow-up questions                    │
└──────────────────▲──────────────────────────────────────┘
                   │ reports + conversation
┌──────────────────┴──────────────────────────────────────┐
│  Layer 2 · Claude Code (analyst)                         │
│  - Reads briefing.md (only data source)                  │
│  - Applies prompts/analyst_*.md                          │
│  - Produces short + long reports                         │
│  - Forbidden: generating any numbers                     │
└──────────────────▲──────────────────────────────────────┘
                   │ data/{TICKER}_{DATE}_briefing.md
┌──────────────────┴──────────────────────────────────────┐
│  Layer 1 · Python data engine                            │
│  fetchers → indicators → scoring → briefing builder      │
└─────────────────────────────────────────────────────────┘
```

### Trigger flow

1. User runs `/analyze NVDA` in Claude Code
2. Slash command runs `python -m stock_analytics NVDA`
3. Python fetches data (or reads cache), computes indicators, scores, writes:
   - `data/NVDA_2026-04-09.json` (machine-readable, complete)
   - `data/NVDA_2026-04-09_briefing.md` (Claude-readable, curated)
4. Slash command instructs Claude to read briefing + prompts, produce reports
5. Short report displayed inline; long report saved to `reports/`
6. User can follow up conversationally (no re-fetch needed)

---

## 5. Module Structure

```
Stock_Analytics/
├── README.md
├── pyproject.toml                  # uv-managed
├── .env.example                    # FINANCIAL_DATASETS_API_KEY
├── .gitignore
│
├── src/stock_analytics/
│   ├── __init__.py
│   ├── cli.py                      # Entry: python -m stock_analytics NVDA
│   │
│   ├── fetchers/                   # External API calls only
│   │   ├── price.py                # yfinance: OHLCV, history
│   │   ├── fundamentals.py         # yfinance + FD API: financials, ratios
│   │   ├── ownership.py            # institutional holdings, insider txns
│   │   ├── analyst.py              # ratings, targets, revisions
│   │   └── news.py                 # recent news + events
│   │
│   ├── indicators/                 # Pure functions, no I/O
│   │   ├── valuation.py            # P/E, PEG, EV/EBITDA, P/S, P/B, simple DCF
│   │   ├── fundamentals.py         # growth, margins, ROE, D/E, FCF margin
│   │   ├── technicals.py           # SMA, EMA, RSI, MACD, volume, 52W
│   │   └── peers.py                # industry median comparison
│   │
│   ├── scoring/
│   │   └── rubric.py               # Indicators → 0–10 scores, transparent rules
│   │
│   ├── briefing/
│   │   ├── builder.py              # JSON → markdown briefing
│   │   └── schema.py               # Pydantic models
│   │
│   └── utils/
│       ├── cache.py                # 1-day cache by ticker
│       └── timeguard.py            # as_of timestamp, look-ahead prevention
│
├── prompts/
│   ├── analyst_short.md            # Short report (Telegram-friendly)
│   ├── analyst_full.md             # Long report (deep read)
│   └── rules.md                    # Shared: no fabrication, must cite, must include counter
│
├── data/                           # gitignored
├── reports/                        # gitignored, plus _index.csv tracking history
│
├── tests/
│   ├── test_indicators.py
│   ├── test_scoring.py
│   └── test_briefing.py
│
└── .claude/
    └── commands/
        └── analyze.md              # /analyze TICKER
```

### Module responsibilities (one-line summary)

| Module | Does | Does NOT |
|---|---|---|
| `fetchers/` | Pull raw data from external APIs | Compute indicators or score |
| `indicators/` | Compute financial/technical indicators | Call APIs or score |
| `scoring/` | Map indicators to 0–10 scores | Compute indicators |
| `briefing/` | Assemble structured markdown for Claude | Compute numbers |
| `prompts/` | Tell Claude how to analyze | Contain data |
| Claude Code | Read briefing, produce narrative reports | Generate any numbers |

---

## 6. Briefing Structure (the critical interface)

The `briefing.md` is the **only** thing Claude sees. Its quality determines the analysis quality.

### Fixed sections

```markdown
# {TICKER} Briefing · as_of: {YYYY-MM-DD HH:MM ET}

> ⚠️ TIMEGUARD: All data through {DATE}. Do not reference events after this date.

## 0 · Snapshot
Company, sector, market cap, price, 52W range, avg volume

## 1 · Fundamentals
- Raw table: Revenue, Gross/Op margin, Net income, FCF, ROE, Net debt/EBITDA (TTM, YoY, 3Y CAGR)
- Derived: growth quality, FCF conversion, balance sheet health
- Score: X / 10
- Rubric hits: explicit list of why this score

## 2 · Valuation
- Multiples table: P/E, Fwd P/E, PEG, EV/EBITDA, P/S vs industry median
- Simple DCF: assumptions explicit (WACC 9%, terminal 3% — defaults), implied fair value
- Score + rubric hits

## 3 · Technicals
- Trend: vs SMA50/SMA200, golden/death cross
- Momentum: RSI, MACD, volume confirmation, distance from 52W high
- Score + rubric hits

## 4 · Sentiment & Flow
- Analyst: consensus, targets, recent revisions
- Insider/institutional flow
- Top 5 news items (last 30d) with sentiment tag
- Score + rubric hits

## 5 · Aggregate
- Weighted composite: F:V:T:S = 30:30:20:20
- Composite score: X.XX / 10

## 6 · Red Flags (auto-detected)
- Programmatic checks: extreme valuation percentile, accelerating insider selling, recent earnings miss, going concern, etc.

## 7 · Data Provenance
- Source + fetch timestamp per data block
```

### Why this structure

1. **Raw → Derived → Score** triple in each section: Claude sees the chain, not just conclusions
2. **Rubric hits explicit**: Claude doesn't guess why a score is high/low; it cites the rule
3. **Aggregate weights in the file**: easy to tune later
4. **Red Flags computed by Python**: certain risks (e.g., "P/S in top 5% historical") shouldn't depend on LLM judgment
5. **Data Provenance**: traceable, signals data freshness
6. **TIMEGUARD at the top**: every Claude pass sees it first, reduces look-ahead bias

---

## 7. Prompt Rules (Claude's constraints)

`prompts/rules.md` (shared by short and full templates):

```
You are analyzing data exclusively from briefing.md. You MUST follow:

1. NO NUMBER GENERATION. Every number in your report must appear verbatim
   in the briefing. If a number is missing, write "data not provided".
   Never estimate, infer, or recall numbers from training data.

2. CITE EVERY CLAIM. Each claim must reference a specific metric from
   the briefing. Format: "Revenue growth strong (TTM +62% YoY, 4 quarters
   of beats)" — not "revenue growth is good".

3. BOTH SIDES REQUIRED. You must produce ≥3 bull arguments AND ≥3 bear
   arguments. If you cannot find one side, explicitly write "counter-
   arguments insufficient — this itself is a risk signal".

4. LEAN + CONFIDENCE + HUMILITY. End with:
   - Lean: {strong buy / lean bull / neutral / lean bear / strong sell}
   - Confidence: 1–10
   - "3 reasons I might be wrong" (mandatory)

5. QUESTIONS FOR THE USER. List 3–5 questions whose answers would change
   the conclusion. These force the user to think, not just consume.

6. NOT AN ADVISOR. Never say "I recommend you buy/sell". You are an
   analyst, not an advisor. The decision belongs to the user.

7. TIMEGUARD. The briefing's as_of date is your knowledge cutoff for
   this analysis. Do not reference events after that date.
```

### Two report templates

- **`analyst_short.md`**: produces ≤ 4096 chars (Telegram-friendly), dashboard format with scores, top 3 bull/bear, lean, top 3 questions
- **`analyst_full.md`**: produces 1500–3000 words, deep dive on each dimension with all rubric hits explained

---

## 8. Scoring Rubric (transparent, tunable)

`scoring/rubric.py` defines **explicit, deterministic** rules. Example for fundamentals:

```python
def score_fundamentals(ind: FundamentalsIndicators) -> ScoreResult:
    score = 5.0
    hits = []

    if ind.revenue_growth_yoy >= 0.30:
        score += 2.0; hits.append("revenue_growth_high(+2)")
    elif ind.revenue_growth_yoy >= 0.10:
        score += 1.0; hits.append("revenue_growth_moderate(+1)")
    elif ind.revenue_growth_yoy < 0:
        score -= 2.0; hits.append("revenue_declining(-2)")

    if ind.fcf_margin >= 0.20:
        score += 1.5; hits.append("fcf_strong(+1.5)")
    # ... etc

    return ScoreResult(value=clamp(score, 0, 10), hits=hits)
```

**Rationale:** scores must be reproducible across runs. LLM-generated scores would be non-deterministic and unauditable.

Aggregate weights (initial): **Fundamentals 30% · Valuation 30% · Technicals 20% · Sentiment 20%**.

---

## 9. Error Handling

| Situation | Behavior |
|---|---|
| Ticker doesn't exist | CLI errors out, no files written |
| yfinance missing financials (small caps) | Field marked `null`, briefing writes "data not provided", scoring downweights that dimension |
| FD API quota exhausted | Fall back to yfinance only, briefing tagged `data_quality: degraded` |
| Anomalous data (e.g., negative P/E) | Pass through unchanged — Claude needs to know the company is unprofitable |
| Claude attempts to cite missing number | Prevented by prompt; caught on user review |
| Cache corruption | Re-fetch, no repair attempted |

**Principle:** Better to give less data than wrong data. LLMs are cautious about missing data but confidently hallucinate around bad data.

---

## 10. Testing Strategy

Targeted, not coverage-driven:

| Target | Method | Why |
|---|---|---|
| `indicators/` | Unit tests with fixed sample data, assert numeric outputs | Most critical — wrong indicators = broken system |
| `scoring/rubric.py` | Unit tests: indicators → score | Prevent regressions when tuning rules |
| `briefing/builder.py` | Mock fetcher output → assert markdown sections | Ensure Claude sees stable format |
| `fetchers/` | **No unit tests.** A `scripts/smoke_test.py` runs them manually | External APIs change; mocks cost more than they're worth |
| Claude report quality | **No automated tests.** User iterates on prompts based on actual outputs | LLM outputs have no ground truth |

---

## 11. Slash Command

`.claude/commands/analyze.md`:

```markdown
---
description: Analyze a US stock ticker, produce short and long reports
argument-hint: <TICKER>
---

Analyze $ARGUMENTS by following these steps:

1. Run: `cd /Users/anguslin/Documents/Claude_Agents/Stock_Analytics && uv run python -m stock_analytics $ARGUMENTS`
2. Confirm `data/$ARGUMENTS_<today>_briefing.md` exists
3. Read the briefing
4. Read `prompts/rules.md`, `prompts/analyst_short.md`, `prompts/analyst_full.md`
5. Strictly follow all rules. Produce both reports.
6. Display the SHORT report inline in this conversation
7. Save the LONG report to `reports/$ARGUMENTS_<today>_full.md`
8. Append a row to `reports/_index.csv`: date, ticker, composite_score, lean
9. End with: report path + "Ask follow-up questions about any dimension."
```

Follow-ups in the same conversation reuse the briefing — no re-fetch.

---

## 12. Dependencies

```toml
[project]
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
dev = ["pytest>=8.0", "pytest-cov"]
```

**No LangChain, no LangGraph, no Anthropic SDK** — Claude Code is the orchestrator.

---

## 13. Decisions on Open Questions

| Question | Decision |
|---|---|
| Multi-ticker comparison? | **v1: no.** Single-ticker depth first. |
| DCF assumption source? | **v1: hard-coded defaults** (WACC 9%, terminal 3%), explicitly displayed in briefing so both Claude and user can critique. |
| Historical record of past analyses? | **Yes.** Reports stay in `reports/`, plus a single-line `reports/_index.csv` per run for quick scanning. |

---

## 14. Out of Scope (explicit non-goals)

- Real-time quotes / streaming data
- Options analysis
- Crypto, forex, futures
- Non-US equities
- Portfolio-level analytics (correlation, factor exposure, VaR)
- Auto-execution of trades
- Push notifications / scheduled runs
- Multi-user / web UI

These may be considered for v2 after v1 has been used in real decisions for a while.

---

## 15. Success Criteria

This project is successful if, after using it for a month, the user can answer YES to:

1. Did it ever surface a bear argument I had missed?
2. Did it ever stop me from buying something on impulse?
3. Did the structured "questions for the user" change how I researched?
4. Are the numbers in every report verifiable against the briefing?
5. Did I avoid any look-ahead bias incidents?

If the answer to any is NO, that's the iteration target.
