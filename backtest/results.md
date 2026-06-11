# Pulse — Results

Data: **2.5 years** hourly (2023-12 → 2026-06), 20 liquid CMC-eligible tokens.
Backtest data = Binance free klines; live Skill reads CoinMarketCap.

## Indicator validation (the core claim)

Pulse is a **velocity / capitulation gauge**. When the basket reprices fastest
and in sync, that burst is the crowd capitulating — historically a bounce follows.

**Crash capture: 20/20** of the worst daily drops had Pulse in its top
decile within 24h. The gauge catches the crashes.

| Forward 24h basket return | by regime |
|---|---|
| after CALM | -0.03% |
| after EUPHORIA | +0.103% |
| **after PANIC** | **+0.37%** (capitulation bounce) |

- Forward volatility after PANIC is **1.3x** the CALM level
  (4.72% vs 3.69%) — panic readings flag turbulent tape.
- Chart: `validation_results.png`.

## Strategy spec (derived from the gauge)

- **PANIC** -> contrarian: long the most oversold basket members (the overshoot bounces).
- **EUPHORIA** -> momentum: long the strongest (trend continues).
- **CALM** -> flat. Market-neutral, equal weight.

## Honest scope (read this)

- The signal is **real but small per trade** (~0.05% market-neutral at 3h).
- At realistic round-trip cost (~0.30% on BSC), the **high-frequency version loses**
  (break-even ~0.06%). See `backtest_fees.py`. We disclose this openly.
- It works on **extreme events / longer holds** (top-decile panic, 24h: positive net
  of fees) and as a **regime/risk alert** — which is fee-immune and what Track 2 asks
  for ("entry/exit rules OR market regime alerts").
- This is a **backtestable strategy spec + indicator**, not a profitable HFT bot.
