"""CLI for the Pulse RAG agent.

Usage (from the pulse/ dir):
    python -m agent ask "How does Pulse catch crashes?"
    python -m agent ask "what's the fee disclosure" --stream
    python -m agent retrieve "euphoria momentum" -k 3
    python -m agent index            # show corpus stats
"""
from __future__ import annotations

import argparse
import sys

# Windows consoles default to cp1252; the corpus has ✅/› etc. Force UTF-8 out.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Load pulse/.env if present so LLM_API_KEY / CMC_API_KEY are available.
try:
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except Exception:
    pass

from . import core
from .rag import get_retriever


def _cmd_ask(args: argparse.Namespace) -> int:
    q = " ".join(args.question)
    if args.stream:
        printed_answer_header = False
        for kind, text in core.ask_stream(q, k=args.k):
            if kind == "sources":
                import json
                srcs = json.loads(text)
                print("Sources:", ", ".join(f"[{s['n']}] {s['citation']}" for s in srcs) or "none")
                print("-" * 60)
            elif kind == "reasoning":
                pass  # hide chain-of-thought in the CLI; available via the API stream
            elif kind == "answer":
                if not printed_answer_header:
                    printed_answer_header = True
                sys.stdout.write(text)
                sys.stdout.flush()
        print()
        return 0
    ans = core.ask(q, k=args.k)
    print(ans.text)
    if ans.sources:
        print("\nSources:")
        for i, s in enumerate(ans.sources, 1):
            print(f"  [{i}] {s.chunk.citation}  (score {s.score:.2f})")
    return 0


def _cmd_retrieve(args: argparse.Namespace) -> int:
    q = " ".join(args.query)
    for i, h in enumerate(core.retrieve(q, k=args.k), 1):
        head = h.chunk.text.replace("\n", " ")[:160]
        print(f"[{i}] {h.chunk.citation}  (score {h.score:.2f})\n    {head}…\n")
    return 0


def _cmd_index(_: argparse.Namespace) -> int:
    r = get_retriever()
    print(f"Corpus: {len(r)} chunks indexed.")
    srcs: dict[str, int] = {}
    for c in r.chunks:
        srcs[c.source] = srcs.get(c.source, 0) + 1
    for src, n in sorted(srcs.items()):
        print(f"  {n:3d}  {src}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="agent", description="Pulse RAG agent")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("ask", help="ask the RAG agent a question")
    a.add_argument("question", nargs="+")
    a.add_argument("-k", type=int, default=5, help="passages to retrieve")
    a.add_argument("--stream", action="store_true", help="stream the answer")
    a.set_defaults(func=_cmd_ask)

    r = sub.add_parser("retrieve", help="show retrieved passages only (no LLM)")
    r.add_argument("query", nargs="+")
    r.add_argument("-k", type=int, default=5)
    r.set_defaults(func=_cmd_retrieve)

    i = sub.add_parser("index", help="show corpus stats")
    i.set_defaults(func=_cmd_index)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
