"""BM25 retrieval over the Pulse knowledge corpus.

Pure-Python (rank-bm25) — no embedding API, no GPU, no network. The corpus is
small (~tens of KB) so lexical BM25 with light query expansion retrieves the
right sections fast and deterministically. Built once at process start.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from rank_bm25 import BM25Okapi

from .corpus import Chunk, load_chunks

_TOKEN = re.compile(r"[a-z0-9]+")

# Domain synonyms so a judge's phrasing hits the right section even when the
# docs use the canonical term (e.g. "crash" -> "drawdown", "vix" -> "velocity").
_EXPAND: dict[str, tuple[str, ...]] = {
    "vix": ("velocity", "volatility", "speed"),
    "crash": ("drawdown", "drop", "capitulation", "panic"),
    "fee": ("cost", "slippage", "transaction"),
    "fees": ("cost", "slippage", "transaction"),
    "regime": ("calm", "panic", "euphoria", "classify"),
    "panic": ("fade_long", "oversold", "capitulation", "bounce", "direction"),
    "euphoria": ("momentum_long", "strongest", "momentum"),
    "calm": ("flat", "stand", "aside"),
    "action": ("fade_long", "momentum_long", "flat", "long", "buy", "signal"),
    "trigger": ("signal", "classify", "emit", "threshold"),
    "signal": ("action", "picks", "fade_long", "momentum_long"),
    "accuracy": ("validation", "backtest", "capture"),
    "edge": ("return", "alpha", "signal"),
    "buy": ("long", "fade", "momentum"),
    "sell": ("short", "flat", "exit"),
    "threshold": ("decile", "percentile", "90th"),
}


def _tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


def _expand(tokens: list[str]) -> list[str]:
    out = list(tokens)
    for t in tokens:
        out.extend(_EXPAND.get(t, ()))
    return out


@dataclass
class Retrieved:
    chunk: Chunk
    score: float


class Retriever:
    """Lexical BM25 retriever over the corpus chunks."""

    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self._bm25 = BM25Okapi([_tokenize(c.text + " " + c.heading) for c in chunks])

    def search(self, query: str, k: int = 5) -> list[Retrieved]:
        if not query.strip():
            return []
        scores = self._bm25.get_scores(_expand(_tokenize(query)))
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        out: list[Retrieved] = []
        for i in ranked[:k]:
            if scores[i] <= 0:
                break
            out.append(Retrieved(self.chunks[i], float(scores[i])))
        return out

    def __len__(self) -> int:
        return len(self.chunks)


@lru_cache(maxsize=1)
def get_retriever() -> Retriever:
    """Process-wide singleton — corpus is read and indexed once."""
    return Retriever(load_chunks())
