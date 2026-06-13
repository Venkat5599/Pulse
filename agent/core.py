"""RAG orchestration: retrieve Pulse knowledge, then answer with DeepSeek.

The agent is grounded — it answers ONLY from retrieved passages and cites them
inline as [1], [2], .... If nothing relevant is retrieved it says so rather than
inventing an answer. This is the deliverable: a retrieval-augmented agent built
on top of the Pulse Velocity-Regime skill.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from . import llm
from .rag import Retrieved, get_retriever

SYSTEM_PROMPT = (
    "You are the Pulse Knowledge Agent — a retrieval-augmented expert on the Pulse "
    "Velocity-Regime trading skill (a 'crypto VIX' that measures how fast and how "
    "synchronized the whole market reprices, classifies the regime CALM / PANIC / "
    "EUPHORIA, and emits a market-neutral signal).\n\n"
    "Answer the user's question USING ONLY the numbered context passages provided. "
    "Cite the passages you use inline as [1], [2], etc. Rules:\n"
    "- If the context does not contain the answer, say so plainly — do NOT invent "
    "numbers, claims, or behavior.\n"
    "- Be concise and concrete (3-6 sentences unless asked for more).\n"
    "- Preserve action semantics exactly: FADE_LONG in PANIC means BUY the oversold "
    "picks expecting a bounce (never 'sell'/'avoid'); MOMENTUM_LONG in EUPHORIA means "
    "BUY the strongest; FLAT in CALM means no trade.\n"
    "- No markdown headers, no 'not financial advice' disclaimers."
)

NO_CONTEXT_MSG = (
    "I don't have anything in the Pulse knowledge base that answers that. "
    "Ask me about the velocity index, the CALM/PANIC/EUPHORIA regimes, the "
    "validation/backtest numbers, the fee disclosure, or how the signal is built."
)


@dataclass
class Answer:
    text: str
    sources: list[Retrieved]


def _build_messages(question: str, hits: list[Retrieved]) -> list[dict]:
    blocks = []
    for i, h in enumerate(hits, 1):
        blocks.append(f"[{i}] ({h.chunk.citation})\n{h.chunk.text}")
    context = "\n\n".join(blocks)
    user = (
        f"Context passages:\n\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer grounded in the passages above, citing [n]."
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def retrieve(question: str, k: int = 6) -> list[Retrieved]:
    return get_retriever().search(question, k=k)


def ask(question: str, *, k: int = 6, max_tokens: int = 1200) -> Answer:
    """Blocking RAG answer."""
    hits = retrieve(question, k=k)
    if not hits:
        return Answer(NO_CONTEXT_MSG, [])
    text = llm.complete(_build_messages(question, hits), max_tokens=max_tokens)
    return Answer(text, hits)


def ask_stream(question: str, *, k: int = 6, max_tokens: int = 1200) -> Iterator[tuple[str, str]]:
    """Streaming RAG answer. Yields ('sources', json)/('reasoning'|'answer', text).

    The first yield is ('sources', <list of citations>) so a UI can show what was
    retrieved before the model speaks. Then reasoning/answer deltas stream through.
    """
    hits = retrieve(question, k=k)
    yield "sources", _sources_payload(hits)
    if not hits:
        yield "answer", NO_CONTEXT_MSG
        return
    yield from llm.stream(_build_messages(question, hits), max_tokens=max_tokens)


def _sources_payload(hits: list[Retrieved]) -> str:
    import json
    return json.dumps([
        {"n": i, "citation": h.chunk.citation, "source": h.chunk.source,
         "score": round(h.score, 3)}
        for i, h in enumerate(hits, 1)
    ])
