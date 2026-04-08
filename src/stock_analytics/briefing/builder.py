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
