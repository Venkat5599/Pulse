# Pulse RAG Agent

A retrieval-augmented agent built on top of the **Pulse Velocity-Regime skill**.
It indexes the skill's own knowledge (SKILL.md, README, `docs/`, the strategy
`scripts/`, backtest results) with **BM25**, retrieves the passages relevant to a
question, and has **DeepSeek V4 Flash** answer **grounded in those passages with
inline citations** — it won't invent numbers it can't cite.

```
question ──▶ BM25 retrieve (top-k chunks) ──▶ DeepSeek V4 Flash (grounded) ──▶ answer + [citations]
                    ▲                                                              │
            corpus: SKILL.md · README · docs/* · scripts/*.py · backtest/results.md
```

## Why BM25, not embeddings
The corpus is small (tens of KB). Lexical BM25 (pure Python, `rank-bm25`) is
deterministic, instant, needs no embedding API / GPU, and retrieves the right
section every time once query synonyms are expanded (`rag.py:_EXPAND`). One less
external dependency to fail in a demo.

## Run locally
```bash
cd pulse
cp agent/.env.example .env        # then put your real LLM_API_KEY in .env
pip install -r agent/requirements.txt

# CLI
python -m agent index                                   # corpus stats
python -m agent ask "How does Pulse catch crashes?"
python -m agent ask "what's the fee disclosure" --stream
python -m agent retrieve "euphoria momentum" -k 3       # retrieval only, no LLM

# HTTP server + chat UI at http://localhost:8080
uvicorn agent.server:app --host 0.0.0.0 --port 8080
```

## API
| Method | Path | Body / returns |
|---|---|---|
| `GET`  | `/health` | `{status, chunks, model}` |
| `GET`  | `/` | minimal chat UI |
| `POST` | `/ask` | `{message, k?}` → `{answer, sources[]}` |
| `POST` | `/ask/stream` | `{message, k?}` → SSE: `sources`, `reasoning`, `answer`, `done` |

## Deploy to the VPS (Docker + nginx)
On the Ubuntu 24.04 VPS, with the `pulse/` repo synced and `pulse/.env` present:
```bash
cd /opt/pulse
bash agent/deploy.sh          # installs Docker if needed, builds, runs, health-checks
```
Serves on port **80** via nginx → the agent container on 8080. Containers
`restart: unless-stopped`, so they survive reboots.

## Files
| File | Role |
|---|---|
| `corpus.py` | load + chunk the knowledge sources (citation = `file › heading`) |
| `rag.py` | BM25 index + retrieval (+ synonym expansion) |
| `llm.py` | DeepSeek V4 Flash client (OpenAI-compatible, blocking + streaming) |
| `core.py` | RAG orchestration: retrieve → grounded prompt → answer |
| `cli.py` / `__main__.py` | `python -m agent …` |
| `server.py` | FastAPI: `/health`, `/ask`, `/ask/stream`, chat UI |
| `Dockerfile`, `docker-compose.yml`, `nginx.conf`, `deploy.sh` | deployment |

> **Secrets:** the API key lives only in `pulse/.env` (gitignored) and is read at
> runtime. Nothing is baked into the image or committed.
