# For the judges — mapped to the Track 2 criteria

Track 2 (Strategy Skills) is scored on four criteria. Here's exactly how Pulse
addresses each, with links to proof. Everything below is live and reproducible.

**Try it in 30 seconds:** ask the live knowledge agent
**https://pulse-agent.187.127.137.136.sslip.io** — _"How does Pulse catch crashes?"_
or run the signal: `python scripts/cmc_live.py`.

---

## 1. Technical execution — _does it work, is it real?_

- ✅ A working **CoinMarketCap AI Agent Hub Skill** (`SKILL.md`) — installs in one
  line across 16 agent platforms (`npx skills add …`).
- ✅ Real **velocity engine** + regime classifier + signal generator — fully
  deterministic and reproducible. ([ARCHITECTURE.md](ARCHITECTURE.md))
- ✅ **Three CMC Agent Hub endpoints** wired live: `quotes/latest` (velocity),
  `fear-and-greed/latest` (conviction), `global-metrics/latest` (BTC dominance +
  total-mcap move as macro context). `cmc_live.py` emits a real signal right now.
- ✅ **Companion RAG agent** (`agent/`) — BM25 retrieval over the skill's own docs
  + DeepSeek V4 Flash, grounded answers with citations. Live + HTTPS (above).
- ✅ Validated on **2.5 years** hourly with a full backtest suite, an
  **out-of-sample split, and a parameter sweep** — not one lucky setting.

## 2. Originality — _a new take on a real problem?_

- ✅ Pulse measures **repricing velocity** — the second derivative — not price level.
  Fear & Greed measures the level; **nobody ships the speed.**
- ✅ CoinMarketCap's own skill library has **no strategy skill and nothing
  velocity-based.** Pulse fills the exact gap. ([METHODOLOGY.md](METHODOLOGY.md))
- ✅ "Crypto VIX as a regime switch" — novel and immediately graspable.

## 3. Real-world relevance — _clear user, path to adoption?_

- ✅ Every trader wants a panic gauge that fires **before** the dump, not after.
- ✅ **20/20 crash capture** over 2.5 years — it demonstrably flags the crashes.
  ([VALIDATION.md](VALIDATION.md))
- ✅ Concrete user loop: **PANIC** → fade oversold / pause DCA; **EUPHORIA** → trim /
  ride momentum; **CALM** → DCA normally. A fundable "crypto fear-velocity index."
- ✅ Ships as an installable Skill any agent can use today.

## 4. Demo & presentation — _is it clear?_

- ✅ **Live site:** https://pulse-vix.vercel.app — the market's heartbeat as a live
  EKG, the 20/20 stat, the honest fee disclosure, and an embedded **ask-the-docs**
  agent.
- ✅ **Live RAG agent:** https://pulse-agent.187.127.137.136.sslip.io (chat UI + API).
- ✅ One-line install + one-question demo ("what's the crypto market regime?").
- ✅ This docs folder: methodology, architecture, validation, FAQ.

---

## The thing we're proudest of: honesty

We **publish the failing PnL.** We tested hard for a fee-surviving trade — naive
HF, conviction-gated deep-panic, directional — and **none beats a realistic 0.30%
BSC round-trip cost** (break-even sits below it, in-sample _and_ out-of-sample).
The gross edge is real; the toll is just bigger. So we don't claim alpha we don't
have. Pulse's value is the **fee-immune regime/capitulation alert** — exactly what
Track 2 invites ("entry/exit rules **or market regime alerts**"). Full numbers:
`backtest/results.md`, `backtest/strategy_gated.py`.

A submission that survives every hard question beats one that looks perfect until
you ask the first one. → [FAQ.md](FAQ.md)
