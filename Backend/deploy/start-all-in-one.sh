#!/bin/sh
# Shared startup for the root all-in-one image on Render and Heroku.
set -eu

# Container platforms may supply their own HOSTNAME. Next.js must bind publicly
# while the API stays on loopback behind its authenticated frontend proxy.
export HOSTNAME=0.0.0.0
export PORT="${PORT:-10000}"

cd /app/backend
if [ "${RUN_MIGRATIONS:-true}" != "false" ]; then
  echo "[start] Applying database migrations (set RUN_MIGRATIONS=false to skip)..."
  alembic upgrade head
else
  echo "[start] RUN_MIGRATIONS=false; skipping database migrations."
fi

echo "[start] Launching API (127.0.0.1:8000), PDF worker and Next.js (0.0.0.0:${PORT})..."
exec supervisord -n -c /etc/supervisor/documind.conf
