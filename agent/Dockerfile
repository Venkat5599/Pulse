# Pulse RAG agent. Build context MUST be the pulse/ repo root so the knowledge
# corpus (docs/, SKILL.md, scripts/, ...) is available to copy:
#   docker build -f agent/Dockerfile -t pulse-rag .
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# Deps first (layer cache).
COPY agent/requirements.txt /app/agent/requirements.txt
RUN pip install --no-cache-dir -r /app/agent/requirements.txt

# The agent package.
COPY agent/ /app/agent/

# Knowledge corpus the retriever indexes at boot (paths mirror corpus.SOURCE_GLOBS).
COPY SKILL.md README.md /app/
COPY docs/ /app/docs/
COPY scripts/ /app/scripts/
COPY backtest/results.md /app/backtest/results.md

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/health',timeout=4).status==200 else 1)"

CMD ["uvicorn", "agent.server:app", "--host", "0.0.0.0", "--port", "8080"]
