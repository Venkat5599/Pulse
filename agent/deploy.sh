#!/usr/bin/env bash
# Deploy the Pulse RAG agent to a fresh Ubuntu 24.04 VPS (Docker + nginx).
# Run this ON the VPS from the synced pulse/ repo root:
#   cd /opt/pulse && bash agent/deploy.sh
# Requires pulse/.env present (LLM_API_KEY etc). Idempotent.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ ! -f .env ]; then
  echo "ERROR: $REPO_ROOT/.env missing. Copy agent/.env.example -> .env and fill LLM_API_KEY." >&2
  exit 1
fi

# Install Docker + compose plugin if absent.
if ! command -v docker >/dev/null 2>&1; then
  echo "[deploy] installing Docker…"
  curl -fsSL https://get.docker.com | sh
fi

echo "[deploy] building + starting containers…"
docker compose -f agent/docker-compose.yml up -d --build

echo "[deploy] waiting for health…"
for i in $(seq 1 30); do
  if curl -fsS http://127.0.0.1/health >/dev/null 2>&1; then
    echo "[deploy] healthy:"; curl -s http://127.0.0.1/health; echo
    exit 0
  fi
  sleep 2
done
echo "[deploy] WARNING: health check did not pass in 60s. Logs:" >&2
docker compose -f agent/docker-compose.yml logs --tail 40
exit 1
