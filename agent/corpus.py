"""Knowledge corpus loader + chunker for the Pulse RAG agent.

Sources are the repo's own docs, the SKILL spec, the README, and the strategy
scripts. Markdown is chunked by heading section (then sub-split if a section is
long) so every chunk carries a human-readable citation: "FILE › Heading".
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# Repo root = parent of this `agent/` package (i.e. the `pulse/` dir).
REPO_ROOT = Path(__file__).resolve().parents[1]

# Knowledge sources, in rough priority order. Globs are relative to REPO_ROOT.
SOURCE_GLOBS: tuple[str, ...] = (
    "SKILL.md",
    "README.md",
    "docs/*.md",
    "backtest/results.md",
    "scripts/*.py",
)

# Target chunk size in characters. Sections larger than this are split on
# paragraph boundaries; smaller adjacent ones are kept whole.
MAX_CHUNK_CHARS = 1100
MIN_CHUNK_CHARS = 60


@dataclass(frozen=True)
class Chunk:
    """A retrievable passage with a citation handle."""
    text: str
    source: str          # e.g. "docs/VALIDATION.md"
    heading: str         # nearest markdown heading, or "" for code/preamble
    chunk_id: int

    @property
    def citation(self) -> str:
        return f"{self.source} › {self.heading}" if self.heading else self.source


def _iter_source_files() -> list[Path]:
    seen: list[Path] = []
    for pattern in SOURCE_GLOBS:
        for p in sorted(REPO_ROOT.glob(pattern)):
            if p.is_file() and p not in seen:
                seen.append(p)
    return seen


def _split_markdown(text: str) -> list[tuple[str, str]]:
    """Split markdown into (heading, body) sections by ATX headings (#..######)."""
    sections: list[tuple[str, str]] = []
    heading = ""
    buf: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^#{1,6}\s+(.*\S)\s*$", line)
        if m:
            if buf:
                sections.append((heading, "\n".join(buf).strip()))
                buf = []
            heading = m.group(1).strip()
        else:
            buf.append(line)
    if buf:
        sections.append((heading, "\n".join(buf).strip()))
    return [(h, b) for h, b in sections if b]


def _split_long(body: str, limit: int = MAX_CHUNK_CHARS) -> list[str]:
    """Greedily pack paragraphs into <=limit-char pieces, never splitting a para."""
    if len(body) <= limit:
        return [body]
    parts: list[str] = []
    cur: list[str] = []
    size = 0
    for para in re.split(r"\n\s*\n", body):
        para = para.strip()
        if not para:
            continue
        if size + len(para) > limit and cur:
            parts.append("\n\n".join(cur))
            cur, size = [], 0
        cur.append(para)
        size += len(para) + 2
    if cur:
        parts.append("\n\n".join(cur))
    return parts


def _docstring(text: str) -> str:
    """Extract a module docstring from a .py file (best-effort, no import)."""
    m = re.match(r'\s*[ru]?("""|\'\'\')(.*?)\1', text, re.DOTALL)
    return m.group(2).strip() if m else ""


def load_chunks() -> list[Chunk]:
    """Read every source file and return the flat list of retrievable chunks."""
    chunks: list[Chunk] = []
    cid = 0
    for path in _iter_source_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        raw = path.read_text(encoding="utf-8", errors="replace")

        if path.suffix == ".py":
            # For code, index the module docstring (the human explanation) plus
            # the source as one fallback chunk so "how is X computed" hits code.
            doc = _docstring(raw)
            if doc:
                for piece in _split_long(doc):
                    chunks.append(Chunk(piece, rel, "module docstring", cid)); cid += 1
            body = raw.strip()
            if len(body) >= MIN_CHUNK_CHARS:
                for piece in _split_long(body, limit=MAX_CHUNK_CHARS * 2):
                    chunks.append(Chunk(piece, rel, "source", cid)); cid += 1
            continue

        for heading, body in _split_markdown(raw):
            if len(body) < MIN_CHUNK_CHARS and not heading:
                continue
            for piece in _split_long(body):
                if len(piece.strip()) < MIN_CHUNK_CHARS:
                    continue
                chunks.append(Chunk(piece.strip(), rel, heading, cid)); cid += 1
    return chunks
