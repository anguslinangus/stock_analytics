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
