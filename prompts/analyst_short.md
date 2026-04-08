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
