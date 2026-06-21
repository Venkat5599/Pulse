---
name: pulse-velocity-regime
description: >
  Pulse turns CoinMarketCap data into a regime-switching crypto trading strategy
  based on market VELOCITY (the speed and synchronization of repricing) rather
  than price level. Computes a "Pulse index" (a crypto VIX), classifies the
  market into CALM / PANIC / EUPHORIA, and emits market-neutral entry/exit rules:
  fade the overshoot in panic, ride momentum in euphoria, stand aside when calm.
license: MIT
metadata:
  track: "BNB Hack — Track 2: Strategy Skills"
  data_source: CoinMarketCap AI Agent Hub
  type: backtestable-strategy-spec
---

# Pulse — the Velocity Regime Skill

> **Fear & Greed tells you the crowd's *mood*. Pulse tells you the crowd's *speed*.**
> Mood is lagging. Speed is leading. Pulse measures how fast and how synchronized
> the whole market reprices at once — the second derivative — and trades the regime.

## Setup (one step)

Set a free CoinMarketCap API key (Basic tier works) before running the live signal:
```bash
export CMC_API_KEY=your_key_here      # get one free at pro.coinmarketcap.com
pip install -r requirements.txt
python scripts/cmc_live.py            # -> live regime + signal JSON
```
Live demo: https://pulse-vix.vercel.app · Repo: https://github.com/Venkat5599/Pulse

## What this Skill does

Given live CoinMarketCap data for a basket of tokens, this Skill:
1. Computes the **Pulse index** — average z-scored move size across the basket.
2. Classifies the **regime**: CALM / PANIC / EUPHORIA.
3. Emits a **market-neutral strategy**: which tokens to long, hold time, stop/TP.

It is a **strategy spec**, not a live-execution agent — no wallet, no signing.

## When to use it

Trigger when the user asks any of:
- "What's the market regime right now?"
- "Is the market panicking / is this a dip to fade?"
- "Give me a crypto trading signal based on volatility / velocity."
- "Run the Pulse strategy on <basket>."
- "How does Pulse work / catch crashes / what's the fee disclosure?" → answer with
  the RAG Knowledge Agent (`agent/`, see "Ask the skill" below), grounded + cited.

## CoinMarketCap data inputs (AI Agent Hub)

Use these CMC endpoints / MCP tools:
- **Latest quotes / OHLCV** — `cryptocurrency/quotes/latest` (and `ohlcv/historical`
  on Hobbyist+ tiers) for recent hourly closes per token. Needed for returns + velocity.
- **Fear & Greed** — `fear-and-greed/latest` — used as a confirming context flag
  (extreme fear strengthens a PANIC fade; extreme greed strengthens EUPHORIA momentum).
- **Derivatives / funding** (optional) — to corroborate regime (crowded longs in euphoria).
- **Trending** (optional) — narrative tilt.

Default basket = liquid CMC-listed tokens (e.g. ETH, XRP, DOGE, ADA, LINK, BCH,
LTC, AVAX, DOT, UNI, ATOM, FIL, INJ, FET, CAKE, TRX, SHIB, TON, AAVE, LDO).

## Algorithm (deterministic core — the LLM orchestrates, math decides)

For each token i over the last ~200 hourly bars:
```
logret_i(t) = ln(close_i(t) / close_i(t-1))
vol_i       = rolling_std(logret_i, window=168)         # 1-week baseline
speed_i(t)  = |logret_i(t)| / vol_i                      # z-scored move size
```
Across the basket at time t:
```
Pulse(t)     = mean_i speed_i(t)                         # the crypto VIX
direction(t) = mean_i logret_i(t)                        # cluster drift
threshold    = 90th percentile of Pulse over the window
regime(t) = CALM      if Pulse(t) <= threshold
            PANIC     if Pulse(t) >  threshold and direction(t) < 0
            EUPHORIA  if Pulse(t) >  threshold and direction(t) >= 0
```
Signal:
```
CALM     -> FLAT (no positions)
PANIC    -> long the 5 most OVERSOLD tokens (most negative last-bar return)
EUPHORIA -> long the 5 STRONGEST tokens (most positive last-bar return)
sizing   -> equal weight, market-neutral; hold 3h; stop -5%; take-profit +6%
```

## Output format

Return JSON the agent can act on or display:
```json
{
  "pulse_index": 1.84,
  "regime": "PANIC",
  "action": "FADE_LONG",
  "picks": ["INJ", "FET", "LDO", "AAVE", "DOT"],
  "fear_greed": 18,
  "hold_hours": 3,
  "stop_loss": -0.05,
  "take_profit": 0.06,
  "sizing": "equal-weight, market-neutral",
  "conviction": {
    "grade": "HIGH",
    "reason": "velocity panic + extreme fear agree (capitulation)",
    "fear_greed": 18,
    "fg_label": "extreme fear"
  }
}
```
Then explain in plain language: the regime, the conviction, and the rationale.

### Conviction layer
The signal is graded by combining the velocity **regime** with CMC's **Fear & Greed**:
PANIC + extreme fear (≤25) or EUPHORIA + extreme greed (≥75) = HIGH conviction
(price and crowd agree). Disagreement = LOW (size down / wait). Both inputs are
CMC-native.

### Optional live bonus — X / social corroboration
For a richer live read, an agent with the **agent-reach** skill can also search
X/Twitter ("search crypto panic/fear on twitter") to corroborate the regime.
Shown in the demo; not hard-wired (free social scrapers are rate-limited).

## Closed-loop agent workflows

Pulse isn't only a one-shot signal — an agent can run it as a **self-pacing closed
loop**: poll the regime, act only when a feedback gate clears, and exit on a defined
condition. Each loop below is `trigger → act → feedback gate → exit`. The agent keeps
looping until its exit condition fires; it does not ask the user between ticks.

### Loop 1 — Regime watch (always-on monitor)
- **Trigger:** every N minutes (default 15) call `/api/heartbeat` (or `cmc_live.py`).
- **Act:** classify CALM / PANIC / EUPHORIA from the live Pulse index.
- **Feedback gate:** only emit an alert when `regime != last_regime` **and**
  `conviction.grade == HIGH` (regime + Fear & Greed agree). Suppress duplicates.
- **Exit:** never auto-exits — long-running watcher. Stops on user halt or market close.
- **Self-pace:** CALM → widen interval (30m); PANIC/EUPHORIA → tighten (5m).

### Loop 2 — Trade lifecycle (entry → manage → exit)
- **Trigger:** Loop 1 fires a HIGH-conviction PANIC or EUPHORIA alert.
- **Act:** open the market-neutral basket (5 picks, equal weight) per the signal.
- **Feedback gate (per tick):** re-poll heartbeat; hold while position is open and
  none of the exits below are hit.
- **Exit (any one):** `hold_hours` (3h) elapsed · stop −5% · take-profit +6% ·
  regime reverts to CALM. On exit → flatten, log result, return to Loop 1.

### Loop 3 — Conviction confirmation (gate before risk)
- **Trigger:** a candidate signal exists but `conviction.grade != HIGH`.
- **Act:** gather corroboration — CMC Fear & Greed delta, and optionally
  **agent-reach** X/Twitter sentiment search.
- **Feedback gate:** promote to HIGH only if ≥2 independent inputs agree
  (velocity + fear/greed + social). Otherwise size down or wait.
- **Exit:** resolves to `confirmed` (→ Loop 2) or `stand_aside` (→ Loop 1), max 3
  retries then default to stand-aside. No infinite loop.

> **Safety:** every loop is read-only signal generation — no wallet, no signing.
> "Act" means emit/track a spec, never execute on-chain. Exit conditions are
> mandatory so an agent always terminates a position-tracking loop.

## How to run

**Live signal (primary — what to run when asked for the regime/signal):**
```bash
export CMC_API_KEY=<your CoinMarketCap key>   # free Basic tier works
python scripts/cmc_live.py                    # -> JSON: regime, action, picks, fear_greed
```
`cmc_live.py` pulls live CoinMarketCap quotes + Fear & Greed, computes the Pulse
index, classifies the regime, and emits the market-neutral signal. This is the
deliverable a judge runs.

**Validation / backtest (reproduce the proof):**
```bash
python scripts/data_fetch.py        # pull history (free Binance klines, no key)
python backtest/validate_indicator.py   # 20/20 crash capture, regime fwd returns
python backtest/backtest_fees.py    # honest fee-survival disclosure
```
Backtest uses Binance free klines (CMC free tier paywalls historical OHLCV);
live path uses CMC. Same regime/signal logic across both; the live high-velocity
threshold is calibrated to the backtest's 90th-percentile decile (2.228), computed
by running the live snapshot proxy over 21,599 historical hourly cross-sections.

**Ask the skill (RAG Knowledge Agent):** a retrieval-augmented agent ships in
`agent/` — it indexes this skill's own docs (SKILL.md, README, `docs/`, the
strategy `scripts/`, backtest results) with BM25 and answers questions grounded in
those passages with inline citations, via DeepSeek V4 Flash. A judge can ask *"how
does Pulse catch crashes?"*, *"what's the fee disclosure?"*, *"what does FADE_LONG
mean?"* and get a cited answer instead of reading every doc.
```bash
cd agent && cp .env.example ../.env   # set LLM_API_KEY (DeepSeek V4 Flash gateway)
pip install -r requirements.txt
python -m agent ask "How does Pulse catch crashes and what was the hit rate?"
# or serve the chat UI + API:
uvicorn agent.server:app --host 0.0.0.0 --port 8080   # /ask, /ask/stream (SSE), /health
```
Live instance: **https://pulse-agent.187.127.137.136.sslip.io** (Docker + nginx +
Caddy auto-TLS on the VPS). Model: `deepseek/deepseek-v4-flash`. Retrieval is
pure-Python BM25 — no embeddings, no GPU.
See `agent/README.md`.

## Validation (2.5y hourly, 20 tokens — see backtest/results.md)

Pulse is validated as a **capitulation / fear gauge**:
- **Crash capture: 20/20** — every one of the worst daily drops had Pulse in its
  top decile within 24h.
- **Forward 24h after PANIC: +0.37%** (capitulation bounce — best of all regimes)
  vs −0.03% after CALM. Panic = contrarian buy.
- Forward volatility after PANIC is **1.3×** the calm level — flags turbulent tape.

**Honest fee disclosure:** the per-trade signal is small (~0.05% at 3h). At realistic
BSC round-trip cost (~0.30%) the high-frequency version loses (break-even ~0.06%,
`backtest_fees.py`). The value is the **regime alert** — fee-immune, and exactly what
Track 2 asks for. We keep the failed naive test (`backtest.py`) in the repo.

## Why it's novel

CoinMarketCap's own skill library has data + report + research skills but **no
strategy/backtest skill, and nothing measuring repricing *velocity*.** Pulse is a
new primitive: a leading "crypto VIX" that drives a regime-switching strategy.
