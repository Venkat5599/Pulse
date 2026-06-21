<p align="center">
  <img src="https://img.shields.io/badge/🫀-Pulse_Velocity_Regime-fb5e6d?style=for-the-badge&labelColor=0a0f12" alt="Pulse Velocity Regime" />
</p>

<h1 align="center">Pulse</h1>

<p align="center">
  <strong>A Regime-Detection Trading Skill for Autonomous Crypto Agents — powered by CoinMarketCap</strong>
</p>

<p align="center">
  <a href="https://pulse-vix.vercel.app">
    <img src="https://img.shields.io/badge/🔴_LIVE-pulse--vix.vercel.app-34d399?style=for-the-badge" alt="Live demo" />
  </a>
  <a href="https://pulse-agent.187.127.137.136.sslip.io">
    <img src="https://img.shields.io/badge/💬_ASK_THE_SKILL-RAG_Agent-00D4FF?style=for-the-badge" alt="RAG agent" />
  </a>
  <img src="https://img.shields.io/badge/Python-3.11-363636?style=for-the-badge&logo=python" alt="Python" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/BNB_Hack-Track_2_Strategy_Skills-fbbf24?style=flat-square" alt="Track 2" />
  <img src="https://img.shields.io/badge/data-CoinMarketCap_AI_Agent_Hub-3B82F6?style=flat-square" alt="CMC" />
  <img src="https://img.shields.io/badge/crash_capture-20%2F20-fb5e6d?style=flat-square" alt="Crash capture" />
  <img src="https://img.shields.io/badge/license-MIT-black?style=flat-square" alt="MIT" />
</p>

---

## 📋 Project Overview

**Pulse** is a strategy Skill that turns live CoinMarketCap data into a regime-switching trading
signal. Every other indicator — Fear & Greed, RSI, sentiment indexes — measures **where price is**.
By the time they move, the crash already happened. Pulse measures **how fast price is moving** — the
speed and synchronization of repricing across a whole basket. That's the *second derivative*, and it
*leads* instead of *lags*.

### What It Does

- **Computes a velocity index** — the "Pulse index", a crypto VIX, from z-scored move sizes
- **Classifies the regime** — `CALM` / `PANIC` / `EUPHORIA`, every hour
- **Switches the strategy** — fade oversold in panic, ride momentum in euphoria, stand aside in calm
- **Grades conviction** — confirms the regime against CMC's Fear & Greed index
- **Emits an actionable signal** — JSON with picks, hold time, stop, take-profit — no wallet, no signing

### Key Innovation

Every other signal reads the **level** of price. Pulse reads its **velocity** — and a burst of fast,
synchronized repricing *is* the crowd capitulating, visible before the bottom prints.

```
Standard signal:  Price Level → Fear & Greed → "the crowd's mood"   (lagging)
Pulse:            Price SPEED → Pulse index  → "the crowd's regime" (leading)
```

It is a **backtestable strategy spec**, not a live-execution agent. Exactly what Track 2 asks for.

---

## 🌐 Why This Matters for the CMC Agent Hub

### The Track 2 Opportunity

Track 2 wants a CMC Skill that turns market data into a trading strategy — a backtestable spec, not a
live-trading agent. CoinMarketCap's own skill library has data, report, and research skills, but
**no strategy skill, and nothing that measures velocity.** Pulse fills that gap.

### What We Bring

| Benefit | Impact |
|---------|--------|
| **A net-new primitive** | A "crypto VIX" measuring repricing speed — not in CMC's skill library |
| **All 3 example builds in one** | Regime-detection + sentiment-divergence + momentum, in a single Skill |
| **CMC-native end to end** | Quotes, Fear & Greed, and global metrics — three Agent Hub endpoints |
| **Honest & fundable** | Discloses its own fee math; the regime alert is the fee-immune product |

### It IS all three Track-2 examples

| Track 2 asked for | Pulse delivers |
|---|---|
| **Regime-detection** that switches strategy | `regime.py` → CALM / PANIC / EUPHORIA, each switches the rule |
| **Sentiment-divergence** flag | `sentiment.py` → velocity vs Fear & Greed; agree = HIGH, disagree = LOW |
| **Momentum** blending indicators into entry/exit | `velocity.py` + `signals.py` → new indicator → entry/exit/sizing |

---

## 🚀 Live Endpoints

| Resource | URL |
|----------|-----|
| **Live demo (the dashboard)** | https://pulse-vix.vercel.app |
| **Ask the Skill (RAG agent)** | https://pulse-agent.187.127.137.136.sslip.io |
| **Repo** | https://github.com/Venkat5599/Pulse |
| **Data source** | https://coinmarketcap.com/api/agent |

### Install the Skill (one line)

```bash
npx skills add https://github.com/Venkat5599/Pulse -y
```
Installs the `pulse-velocity-regime` Skill into Claude Code, Cursor, Codex, Gemini CLI + 12 more.

---

## 📖 How to Use

### Option 1: Live signal (the deliverable a judge runs)

```bash
export CMC_API_KEY=your_key            # free Basic tier at pro.coinmarketcap.com
pip install -r requirements.txt
python scripts/cmc_live.py
```

Output — an actionable signal JSON:

```jsonc
{
  "source": "CoinMarketCap AI Agent Hub (quotes/latest + fear-and-greed + global-metrics)",
  "pulse_index": 2.41,
  "direction_1h": -1.83,
  "regime": "PANIC",
  "action": "FADE_LONG",
  "picks": ["INJ", "FET", "LDO", "AAVE", "DOT"],
  "fear_greed": 18,
  "btc_dominance": 54.7,
  "total_mcap_change_24h": -6.2,
  "hold_hours": 3,
  "stop_loss": -0.05,
  "take_profit": 0.06,
  "sizing": "equal-weight, market-neutral",
  "conviction": { "grade": "HIGH", "reason": "velocity panic + extreme fear agree (capitulation)" }
}
```

### Option 2: Python integration

```python
import pandas as pd
from scripts.velocity import compute, load_panel
from scripts.signals import generate, to_dict

# 1. Build the velocity panel + regime from OHLCV
panel = load_panel()                 # hourly OHLCV per symbol
agg   = compute(panel)               # adds pulse, direction, regime per timestamp
row   = agg.iloc[-1]                 # latest bar

# 2. Generate the market-neutral signal for that regime
last_returns = panel.groupby("symbol")["close"].apply(
    lambda s: s.pct_change().iloc[-1])
signal = generate(row["regime"], last_returns)

print(to_dict(signal))
# { "regime": "PANIC", "action": "FADE_LONG", "picks": [...],
#   "hold_hours": 3, "stop_loss": -0.05, "take_profit": 0.06, ... }
```

### Option 3: Ask the Skill (RAG agent)

For grounded, cited answers about the strategy — no need to read every doc.

```bash
cd agent && cp .env.example ../.env          # set LLM_API_KEY
pip install -r requirements.txt
python -m agent ask "How does Pulse catch crashes and what was the hit rate?"

# or serve the chat UI + API:
uvicorn agent.server:app --host 0.0.0.0 --port 8080   # /ask, /ask/stream (SSE), /health
```

Pure-Python **BM25** retrieval over the Skill's own docs + answer via **DeepSeek V4 Flash**.
A judge can ask *"what's the fee disclosure?"* or *"what does FADE_LONG mean?"* and get a cited reply.

### Module Reference

| Module | Description | Entry point |
|--------|-------------|-------------|
| `scripts/velocity.py` | Computes the Pulse index + per-timestamp regime | `compute(df)` |
| `scripts/regime.py` | CALM / PANIC / EUPHORIA classifier | `classify(pulse, direction, threshold)` |
| `scripts/signals.py` | Entry / exit / sizing rules per regime | `generate(regime, last_returns)` |
| `scripts/sentiment.py` | Conviction layer (regime + Fear & Greed) | `conviction(regime, fear_greed)` |
| `scripts/cmc_live.py` | Live signal from CoinMarketCap | `python scripts/cmc_live.py` |
| `scripts/data_fetch.py` | Historical OHLCV (free Binance klines, no key) | `python scripts/data_fetch.py` |

---

## 🛡️ Strategy Rules (the regime engine)

One velocity index drives a state machine. Each regime switches the rule deterministically — the LLM
orchestrates, the math decides.

| Regime | Trigger | Action | Picks | Hold | Stop | Take-Profit |
|--------|---------|--------|-------|------|------|-------------|
| **CALM** | Pulse ≤ threshold | `FLAT` — stand aside | — | — | — | — |
| **PANIC** | Pulse > threshold **and** cluster falling | `FADE_LONG` — fade the overshoot | 5 most oversold | 3h | −5% | +6% |
| **EUPHORIA** | Pulse > threshold **and** cluster rising | `MOMENTUM_LONG` — ride the trend | 5 strongest | 3h | −5% | +6% |

All positions: **equal-weight, market-neutral**. The high-velocity threshold (`2.228`) is the
backtest-calibrated 90th-percentile decile over 21,599 historical hourly cross-sections.

### Conviction grading (the divergence gate)

```
PANIC    + extreme fear  (F&G ≤ 25)  → HIGH   (capitulation — price and crowd agree)
EUPHORIA + extreme greed (F&G ≥ 75)  → HIGH   (momentum — price and crowd agree)
agreement-ish                        → MEDIUM
disagreement                         → LOW    (size down / wait)
```

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                         USER / AGENT (natural language)                 │
│              "What's the crypto market regime right now?"               │
└────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│              CoinMarketCap AI Agent Hub                                  │
│        quotes/latest  ·  fear-and-greed  ·  global-metrics              │
└────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       Velocity engine  (velocity.py)                    │
│        speed_i = |log_return_i| / rolling_std_i   →   Pulse index       │
└────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    Regime classifier  (regime.py)                       │
│        CALM   ·   PANIC (fast + falling)   ·   EUPHORIA (fast + rising) │
└────────────────────────────────────────────────────────────────────────┘
              │                       │                       │
              ▼                       ▼                       ▼
   ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
   │   CALM → FLAT      │  │  PANIC → FADE_LONG │  │ EUPHORIA → MOMENTUM│
   │   stand aside      │  │  long oversold x5  │  │  long strongest x5 │
   └────────────────────┘  └────────────────────┘  └────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│            Conviction layer  (sentiment.py)  +  CMC Fear & Greed         │
│        velocity + sentiment agree → HIGH   ·   disagree → LOW (wait)    │
└────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                    Signal JSON  ·  regime · picks · conviction
```

**The math** (per token `i`, hourly):
```
speed_i  = |log_return_i| / rolling_std_i        # z-scored move size (168h vol baseline)
Pulse    = mean_i speed_i                          # the crypto VIX
regime   = CALM | PANIC (fast+falling) | EUPHORIA (fast+rising)   # 90th-percentile threshold
```

---

## 🔥 The Proof — it catches every crash

Validated on **2.5 years** of hourly data, 20 liquid CMC-eligible tokens (21,599 cross-sections).

<div align="center">

### `20 / 20`
**Of the 20 worst daily drops, Pulse was in its top decile within 24h. Every single one.**

</div>

| Forward 24h return | by regime | read |
|---|---|---|
| after `CALM` | −0.03% | quiet → nothing |
| after `EUPHORIA` | +0.103% | greed → momentum |
| after **`PANIC`** | **+0.37%** | **capitulation → the bounce** |

Forward volatility after panic is **1.3×** the calm level. → [full methodology](docs/VALIDATION.md)

### We disclose our own fee math (the honest part)

- The raw per-trade signal is **real but small** (~0.05% market-neutral at 3h).
- At realistic BSC round-trip cost (~0.30%), the **high-frequency version loses** — break-even is
  only **~0.06%**. We keep the failed test (`backtest/backtest.py`) **in the repo on purpose.**
- ✅ The value is the **regime alert itself** — a *fee-immune capitulation gauge*. Track 2 asks for
  *"entry/exit rules OR market regime alerts."* Pulse is the gauge, validated.

---

## 🧪 Testing & Reproduce the Proof

```bash
# Pull history (free Binance klines, no key)
python scripts/data_fetch.py

# Run the validation suite
python backtest/validate_indicator.py     # 20/20 crash capture, regime forward returns
python backtest/backtest_fees.py          # honest fee-survival disclosure

# Expected highlights:
#  ✅ Crash capture: 20/20 worst drops had Pulse in top decile within 24h
#  ✅ Forward 24h after PANIC: +0.37% (best of all regimes)
#  ❌ Naive high-frequency backtest LOSES after 0.30% fees (kept on purpose)
```

Backtest uses Binance free klines (CMC free tier paywalls historical OHLCV); the live path uses CMC.
Same regime/signal logic across both.

---

## 📁 Project Structure

```
pulse/
├── SKILL.md                  # ⭐ the CMC AI Agent Hub Skill (the deliverable)
├── scripts/                  # the strategy engine (velocity, regime, signals, sentiment, live)
├── backtest/                 # validation + honest fee disclosure
│   ├── validate_indicator.py # ⭐ 20/20 crash-capture proof
│   └── backtest.py           # naive test — FAILS (kept for honesty)
├── agent/                    # 💬 BM25 RAG knowledge agent (DeepSeek V4 Flash)
├── site/                     # the live Vercel demo
└── docs/                     # 📚 methodology, architecture, validation, judges' map
```

---

## 📚 Documentation

- [METHODOLOGY.md](docs/METHODOLOGY.md) — the thesis: why speed leads mood
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — the system, the math, the data flow
- [VALIDATION.md](docs/VALIDATION.md) — every number, every test, honestly
- [JUDGES.md](docs/JUDGES.md) — mapped to the 4 Track-2 criteria
- [FAQ.md](docs/FAQ.md) — the hard questions, answered

---

## 🛠️ Tech Stack

- **Strategy:** Python 3.11, pandas, numpy — deterministic core
- **Data:** CoinMarketCap AI Agent Hub (live) · Binance free klines (backtest)
- **Knowledge agent:** pure-Python BM25 retrieval + DeepSeek V4 Flash, FastAPI + SSE
- **Demo site:** Vercel static deploy
- **Infra:** Docker + nginx + Caddy (auto-HTTPS), single-VPS deploy

---

## 📈 Roadmap

- [x] Velocity index + regime classifier
- [x] Market-neutral signal rules (entry / exit / sizing)
- [x] Conviction layer (regime + Fear & Greed)
- [x] 2.5-year backtest — 20/20 crash capture
- [x] Honest fee disclosure (failing test kept in repo)
- [x] Live CMC signal path (`cmc_live.py`)
- [x] RAG knowledge agent (BM25 + DeepSeek V4 Flash)
- [x] Live Vercel demo
- [ ] Liquidity-weighted Pulse index
- [ ] Derivatives/funding confirmation layer
- [ ] Multi-basket presets (majors / DeFi / memes)

---

<div align="center">

## Every crash leaves the same fingerprint. Pulse reads it first.

**Built for BNB Hack: AI Trading Agent Edition** · CoinMarketCap × Trust Wallet × BNB Chain

🫀 [Live demo](https://pulse-vix.vercel.app) · 💬 [Ask the Skill](https://pulse-agent.187.127.137.136.sslip.io) · 📚 [Docs](docs/)

### License
MIT — see [LICENSE](LICENSE).

</div>
