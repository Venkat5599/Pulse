"""
Pulse — fees-aware backtest (credibility).

The +18.74% headline is gross. Judges will ask: does it survive costs?
This applies realistic round-trip costs and sweeps fee levels so we can state
the honest break-even.

Costs per trade (round trip = enter + exit):
  - taker fee:        ~0.10% each side on BSC CEX/DEX -> 0.20% round trip
  - slippage:         ~0.05% each side on liquid pairs -> 0.10% round trip
  Default total drag ~0.30% round trip per position.

Strategy: locked rules (PANIC->fade5, EUPHORIA->mom5, 3h, market-neutral,
non-overlapping). We charge the cost on every position opened.
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from velocity import load_panel, compute  # noqa: E402

HOLD, K = 3, 5
FEE_LEVELS = [0.0, 0.10, 0.20, 0.30, 0.40, 0.50]  # % round-trip per position


def basket_returns() -> pd.Series:
    raw = load_panel()
    agg = compute(raw)
    panel = raw.sort_values(["symbol", "time"]).copy()
    panel["fwd"] = panel.groupby("symbol")["close"].transform(lambda s: s.shift(-HOLD) / s - 1)
    panel["lastret"] = panel.groupby("symbol")["close"].transform(lambda s: s / s.shift(1) - 1)
    panel["mkt_fwd"] = panel.groupby("time")["fwd"].transform("mean")
    panel["rel_fwd"] = panel["fwd"] - panel["mkt_fwd"]
    panel = panel.merge(agg[["regime"]].reset_index(), on="time", how="left")

    def bar(g):
        reg = g["regime"].iloc[0]
        if reg == "PANIC":
            return g.nsmallest(K, "lastret")["rel_fwd"].mean()
        if reg == "EUPHORIA":
            return g.nlargest(K, "lastret")["rel_fwd"].mean()
        return np.nan

    by_bar = panel.groupby("time", group_keys=False).apply(bar).dropna()
    return by_bar.iloc[::HOLD]  # non-overlapping


def main() -> None:
    trades = basket_returns()
    n = len(trades)
    print("=" * 60)
    print("PULSE — FEES-AWARE BACKTEST")
    print(f"{n} non-overlapping trades, market-neutral, 3h hold")
    print("=" * 60)
    print(f"{'fee% rt':>8} | {'net return':>11} | {'sharpe':>7} | {'maxDD':>7} | {'win%':>5}")
    print("-" * 60)
    rows = []
    for fee in FEE_LEVELS:
        net = trades - fee / 100.0          # charge cost per opened position
        eq = (1 + net.fillna(0)).cumprod()
        ret = (eq.iloc[-1] - 1) * 100
        sharpe = net.mean() / (net.std() + 1e-12) * np.sqrt(24 / HOLD * 365)
        mdd = (eq / eq.cummax() - 1).min() * 100
        win = (net > 0).mean() * 100
        rows.append((fee, ret, sharpe, mdd, win))
        print(f"{fee:>8.2f} | {ret:>+10.2f}% | {sharpe:>7.2f} | {mdd:>6.2f}% | {win:>4.1f}")
    print("-" * 60)
    # break-even fee (where net return crosses 0)
    be = None
    for i in range(1, len(rows)):
        if rows[i-1][1] > 0 >= rows[i][1]:
            f0, r0 = rows[i-1][0], rows[i-1][1]
            f1, r1 = rows[i][0], rows[i][1]
            be = f0 + (f1 - f0) * r0 / (r0 - r1)
            break
    print(f"Break-even round-trip cost: {'%.3f%%' % be if be else '> %.2f%%' % FEE_LEVELS[-1]}")
    print("Typical BSC liquid round-trip cost ~0.30%. Verdict:",
          "SURVIVES" if (be and be > 0.30) else "tight — favor lower-cost venues/limit orders")
    print("=" * 60)

    # write to results.md (append)
    md = ["\n## Fees-aware results (round-trip cost per position)\n",
          "| fee% rt | net return | Sharpe | maxDD | win% |",
          "|---|---|---|---|---|"]
    for fee, ret, sharpe, mdd, win in rows:
        md.append(f"| {fee:.2f}% | {ret:+.2f}% | {sharpe:.2f} | {mdd:.2f}% | {win:.1f}% |")
    md.append(f"\n**Break-even round-trip cost: "
              f"{'%.3f%%' % be if be else '>%.2f%%' % FEE_LEVELS[-1]}** "
              f"(typical BSC liquid ~0.30%).")
    (ROOT / "backtest" / "results.md").open("a", encoding="utf-8").write("\n".join(md) + "\n")
    print("Appended to results.md")


if __name__ == "__main__":
    main()
