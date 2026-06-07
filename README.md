# Pulse — the crypto velocity regime Skill

> **CoinMarketCap's Fear & Greed measures the crowd's *mood*. Pulse measures the crowd's *speed*.**
> A CMC AI Agent Hub Skill for **BNB Hack — Track 2: Strategy Skills**.

Mood is a level — it tells you where sentiment *is*, after the fact. **Speed is leading** —
how fast and how synchronized the whole market reprices *right now*. When dozens of tokens
move abnormally hard at once, that burst is the crowd panicking (or euphoric). Panic
overshoots and reverts; euphoria trends. Pulse measures that speed, names the regime, and
emits a market-neutral strategy.

## The idea in one picture
`speed_i = |return_i| / its_own_volatility` → average across the basket = **Pulse index**
(a "crypto VIX"). High Pulse + falling = **PANIC** (fade the overshoot). High Pulse +
rising = **EUPHORIA** (ride momentum). Low Pulse = **CALM** (stand aside).

![results](backtest/pulse_results.png)

## Why it's new
CoinMarketCap's official skill library has data, report, and research skills — but **no
strategy/backtest skill, and nothing that measures repricing *velocity*.** Pulse is a new
primitive: a *leading* volatility-regime gauge that drives a switchable strategy. F&G is
the lagging cousin; Pulse is the derivative.

## What's in here
```
SKILL.md                  # the LLM Skill (CMC AI Agent Hub format) — the deliverable
scripts/
  data_fetch.py           # historical OHLCV (Binance free klines for backtest)
  velocity.py             # the Pulse index
  regime.py               # CALM / PANIC / EUPHORIA classifier
  signals.py              # entry/exit/sizing rules
  cmc_live.py             # live signal from CoinMarketCap AI Agent Hub
backtest/
  backtest.py             # v1 naive test — FAILS (kept for honesty)
  backtest2.py            # v2 market-neutral test — edge found
  backtest_fees.py        # fee-survival test (HF version loses — disclosed)
  backtest_extreme.py     # extreme-event sweep
  validate_indicator.py   # the core proof: 20/20 crash capture
  make_results.py / export_web_data.py
  results.md              # consolidated results
  validation_results.png  # the money chart
```

## Validation (2.5y hourly, 20 liquid CMC-eligible tokens)
| Result | Value |
|---|---|
| **Crash capture** | **20/20** of the worst daily drops had Pulse in its top decile within 24h |
| Forward 24h after PANIC | **+0.385%** (capitulation bounce — the contrarian edge) |
| Forward 24h after CALM | −0.026% |
| Forward 24h after EUPHORIA | +0.106% |
| Forward vol after PANIC | 1.3× the calm level (flags turbulence) |

**Honest scope (we disclose this openly):** the per-trade signal is real but small
(~0.05% market-neutral at 3h). At realistic BSC round-trip cost (~0.30%) the
**high-frequency version loses** (break-even ~0.06%) — see `backtest/backtest_fees.py`,
and the failed naive test in `backtest/backtest.py`. The value is the **regime signal**:
a fee-immune capitulation gauge. Track 2 explicitly asks for "entry/exit rules **or
market regime alerts**" — Pulse is the latter, validated. This is a *backtestable
strategy spec + indicator*, not a profitable HFT bot.

## Run it
```bash
pip install -r requirements.txt
python scripts/data_fetch.py     # pull data (free, no key)
python scripts/velocity.py       # Pulse index + regimes
python backtest/backtest2.py     # validate the edge
python backtest/make_results.py  # equity curve + chart
```

## Live data
The backtest uses Binance free klines (CMC's free tier paywalls historical OHLCV).
The live Skill reads **CoinMarketCap AI Agent Hub** (quotes, Fear & Greed, derivatives,
trending) — identical strategy logic. See `SKILL.md`.

## License
MIT.
