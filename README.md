<p align="center">
  <img src="https://img.shields.io/badge/🫀-Pulse-fb5e6d?style=for-the-badge&labelColor=0a0f12" alt="Pulse" />
</p>

<h1 align="center">Pulse</h1>

<p align="center">
  <strong>The crypto market has a heartbeat. Pulse reads it.</strong>
</p>

<p align="center">
  A regime-detection trading Skill that measures market <strong>velocity</strong> — the speed and
  synchronization of repricing — names the regime (<strong>CALM · PANIC · EUPHORIA</strong>),
  and turns it into a backtestable, fee-honest strategy. Built as a
  <strong>CoinMarketCap AI Agent Hub Skill</strong>.
</p>

<p align="center">
  <a href="https://pulse-vix.vercel.app">
    <img src="https://img.shields.io/badge/🔴_LIVE-pulse--vix.vercel.app-34d399?style=for-the-badge" alt="Live demo" />
  </a>
  <img src="https://img.shields.io/badge/Crash_Capture-20%2F20-fb5e6d?style=for-the-badge" alt="Crash capture" />
  <img src="https://img.shields.io/badge/Python_·_BM25_RAG-363636?style=for-the-badge&logo=python" alt="Python" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/BNB_Hack-Track_2_Strategy_Skills-fbbf24?style=flat-square" alt="Track 2" />
  <img src="https://img.shields.io/badge/data-CoinMarketCap_AI_Agent_Hub-3B82F6?style=flat-square" alt="CMC" />
  <img src="https://img.shields.io/badge/backtest-2.5_years_hourly-success?style=flat-square" alt="Backtest" />
  <img src="https://img.shields.io/badge/license-MIT-black?style=flat-square" alt="MIT" />
</p>

---

## 📋 Overview

**Pulse** is an autonomous regime-detection Skill for crypto. Every other signal — Fear & Greed,
RSI, sentiment indexes — measures **where price is**. By the time they move, the crash already
happened. Pulse measures **how fast price is moving** — the second derivative — so the signal
*leads* instead of *lags*.

> **Fear & Greed tells you the crowd's _mood_. Pulse tells you the crowd's _speed_.**
> Mood is lagging. Speed is leading.

Given live CoinMarketCap data for a basket of tokens, Pulse:

1. Computes the **Pulse index** — average z-scored move size across the basket (a "crypto VIX").
2. Classifies the **regime** — `CALM` / `PANIC` / `EUPHORIA`.
3. Emits a **market-neutral strategy** — which tokens to long, hold time, stop/take-profit.
4. Grades **conviction** by confirming the regime against CMC's Fear & Greed index.

It is a **backtestable strategy spec**, not a live-execution agent — no wallet, no signing,
no money. Exactly what Track 2 asks for.

### The agent *decides* — it doesn't just signal

Pulse runs as a self-pacing closed loop: poll the regime, act only when a feedback gate clears
(`regime != last_regime` **and** conviction is HIGH), and exit on a defined condition
(hold elapsed · stop · take-profit · regime reverts). It suppresses duplicates, widens its
interval in calm, tightens it in panic, and never asks a human between ticks. That is
agent-native behavior.

---

## 🧠 Why this is different

Every other signal looks at **where price is**. Pulse looks at **how fast it's moving** — the
*second derivative*.

| | Fear & Greed (the standard) | 🫀 **Pulse** (this) |
|---|---|---|
| Measures | sentiment **level** | repricing **speed + synchronization** |
| Nature | **lagging** | **leading** |
| Output | a number 0–100 | a **regime** + a **strategy** |
| In CMC's skill library? | ✅ | ❌ **(this fills the gap)** |

CoinMarketCap's official skill repo has data, report, and research skills — but **no strategy
skill, and nothing that measures velocity.** Pulse is a new primitive.

### It's all three Track-2 example builds in one

| Track 2 asked for | Pulse delivers |
|---|---|
| **Regime-detection** that switches strategy | `regime.py` → CALM / PANIC / EUPHORIA, each switches the rule |
| **Sentiment-divergence** flag | `sentiment.py` → velocity vs Fear & Greed; agree = HIGH, disagree = LOW |
| **Momentum** blending indicators into entry/exit | `velocity.py` + `signals.py` → new indicator → entry/exit/sizing |

---

## 🔥 The proof — it catches every crash

Validated on **2.5 years** of hourly data, 20 liquid CMC-eligible tokens (21,599 hourly
cross-sections).

<div align="center">

### `20 / 20`
**Of the 20 worst daily drops, Pulse was in its top decile within 24h. Every single one.**

</div>

| Forward 24h return | by regime | read |
|---|---|---|
| after `CALM` | −0.03% | quiet → nothing |
| after `EUPHORIA` | +0.103% | greed → momentum |
| after **`PANIC`** | **+0.37%** | **capitulation → the bounce** |

Panic readings are followed by the **best** forward returns — capitulation, then mean-reversion.
Forward volatility after panic is **1.3×** the calm level. → [full methodology](docs/VALIDATION.md)

---

## 🪙 We disclose our own fee math (the honest part)

Most "winning strategy" submissions quietly skip transaction costs. We don't.

- The raw per-trade signal is **real but small** (~0.05% market-neutral at 3h).
- At realistic BSC round-trip cost (~0.30%), the **high-frequency version loses** — break-even is
  only **~0.06%**. We keep the failed test (`backtest/backtest.py`) **in the repo on purpose.**
- ✅ The value is the **regime signal itself** — a *fee-immune capitulation gauge*. Track 2
  explicitly asks for **"entry/exit rules OR market regime alerts."** Pulse is the gauge, validated.

> A fragile strategy dressed as a money-printer dies under one judge question. An honest,
> validated indicator that discloses its own limits earns trust. We chose the second.

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
│              CoinMarketCap AI Agent Hub  (quotes + Fear & Greed)        │
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
│            Conviction layer  (sentiment.py)  + CMC Fear & Greed          │
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
→ [architecture deep-dive](docs/ARCHITECTURE.md)

---

## ⚡ Install in one line

```bash
npx skills add https://github.com/Venkat5599/Pulse -y
```
Installs the `pulse-velocity-regime` Skill into Claude Code, Cursor, Codex, Gemini CLI + 12 more.

**Run the live signal:**
```bash
export CMC_API_KEY=your_key            # free at pro.coinmarketcap.com
pip install -r requirements.txt
python scripts/cmc_live.py
```
```jsonc
{ "regime": "PANIC", "action": "FADE_LONG",
  "picks": ["INJ","FET","LDO","AAVE","DOT"],
  "fear_greed": 18,
  "conviction": { "grade": "HIGH", "reason": "velocity panic + extreme fear agree" } }
```

**Or just ask your agent:** _"What's the crypto market regime right now?"_

---

## 💬 Ask the Skill (RAG Knowledge Agent)

A retrieval-augmented agent ships in `agent/`. It indexes Pulse's own docs (SKILL.md, README,
`docs/`, the strategy `scripts/`, backtest results) with **pure-Python BM25** — no embeddings,
no GPU — and answers questions grounded in those passages with inline citations, via
**DeepSeek V4 Flash**.

```bash
cd agent && cp .env.example ../.env          # set LLM_API_KEY
pip install -r requirements.txt
python -m agent ask "How does Pulse catch crashes and what was the hit rate?"

# or serve the chat UI + API:
uvicorn agent.server:app --host 0.0.0.0 --port 8080   # /ask, /ask/stream (SSE), /health
```

**Live instance:** https://pulse-agent.187.127.137.136.sslip.io
(Docker + nginx + Caddy auto-TLS on a single VPS · model `deepseek/deepseek-v4-flash`)

A judge can ask *"how does Pulse catch crashes?"*, *"what's the fee disclosure?"*,
*"what does FADE_LONG mean?"* and get a cited answer instead of reading every doc.

---

## 🚀 How to run

```bash
# Live signal (primary — the deliverable a judge runs)
export CMC_API_KEY=<your CoinMarketCap key>   # free Basic tier works
python scripts/cmc_live.py                    # -> JSON: regime, action, picks, fear_greed

# Validation / backtest (reproduce the proof)
python scripts/data_fetch.py                  # pull history (free Binance klines, no key)
python backtest/validate_indicator.py         # 20/20 crash capture, regime forward returns
python backtest/backtest_fees.py              # honest fee-survival disclosure
```

Backtest uses Binance free klines (CMC free tier paywalls historical OHLCV); the live path uses
CMC. Same regime/signal logic across both; the live high-velocity threshold (2.228) is calibrated
to the backtest's 90th-percentile decile.

---

## 📂 What's inside

```
pulse/
├── SKILL.md                  # ⭐ the CMC AI Agent Hub Skill (the deliverable)
├── scripts/
│   ├── velocity.py           # the Pulse index
│   ├── regime.py             # CALM / PANIC / EUPHORIA classifier
│   ├── signals.py            # entry / exit / sizing rules
│   ├── sentiment.py          # conviction layer (regime + Fear & Greed)
│   ├── cmc_live.py           # live signal from CoinMarketCap
│   └── data_fetch.py         # historical OHLCV (free, no key)
├── backtest/
│   ├── validate_indicator.py # ⭐ 20/20 crash-capture proof
│   ├── backtest.py           # naive test — FAILS (kept for honesty)
│   ├── backtest_fees.py      # fee-survival disclosure
│   └── results.md            # consolidated numbers
├── agent/                    # 💬 BM25 RAG knowledge agent (DeepSeek V4 Flash)
├── site/                     # the live Vercel demo
└── docs/                     # 📚 methodology, architecture, validation, judges' map
```

---

## 🛠️ Tech Stack

- **Strategy:** Python, pandas, numpy — deterministic core; the LLM orchestrates, the math decides
- **Data:** CoinMarketCap AI Agent Hub (live) · Binance free klines (backtest)
- **Knowledge agent:** pure-Python BM25 retrieval + DeepSeek V4 Flash, FastAPI + SSE streaming
- **Demo site:** Vercel static deploy
- **Infra:** Docker + nginx + Caddy (auto-HTTPS), single-VPS deploy

---

## 📚 Docs

| Doc | What |
|---|---|
| [docs/METHODOLOGY.md](docs/METHODOLOGY.md) | The thesis: why speed leads mood |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | The system, the math, the data flow |
| [docs/VALIDATION.md](docs/VALIDATION.md) | Every number, every test, honestly |
| [docs/JUDGES.md](docs/JUDGES.md) | Mapped to the 4 Track-2 criteria |
| [docs/FAQ.md](docs/FAQ.md) | The hard questions, answered |

---

## 🔗 Links

| Resource | URL |
|----------|-----|
| **Live demo** | https://pulse-vix.vercel.app |
| **Ask the Skill (RAG agent)** | https://pulse-agent.187.127.137.136.sslip.io |
| **Repo** | https://github.com/Venkat5599/Pulse |
| **Data source** | https://coinmarketcap.com/api/agent |

---

<div align="center">

## Every crash leaves the same fingerprint. Pulse reads it first.

**Built for BNB Hack: AI Trading Agent Edition** · CoinMarketCap × Trust Wallet × BNB Chain

🫀 [Live demo](https://pulse-vix.vercel.app) · 📦 [Install](#-install-in-one-line) · 📚 [Docs](docs/)

### License
MIT — see [LICENSE](LICENSE).

</div>
