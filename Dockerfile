# =============================================================================
# DocuMind / NoteMind — all-in-one image for Render and Heroku
#
# One container runs the whole stack on the platform's assigned $PORT:
#
#   Internet ──► Next.js standalone frontend   0.0.0.0:${PORT:-10000}  (public)
#                    │  /api/backend proxy (BACKEND_URL=http://127.0.0.1:8000)
#                    ▼
#                FastAPI (uvicorn)             127.0.0.1:8000           (internal)
#                PDF worker (python -m app.workers.pdf_worker)           (internal)
#
# On container start, Alembic migrations are applied automatically
# (set RUN_MIGRATIONS=false to skip and manage the schema yourself).
# Supervisor restarts the API/worker/web server if any of them exits.
#
# Build context is the repository root:
#   docker build -t documind-allinone .
# On Render: Language "Docker", Dockerfile path ./Dockerfile, context .
# On Heroku: heroku.yml builds this image; app.json selects the container stack.
# Heroku runs migrations in its release phase and sets RUN_MIGRATIONS=false.
# =============================================================================

# ----------------------------------------------------------------------------
# Stage 1 — backend Python environment (wheels compiled here, glibc)
# ----------------------------------------------------------------------------
FROM python:3.12-slim-bookworm AS backend-deps

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY Backend/requirements.txt ./
RUN pip install --upgrade pip setuptools wheel \
 && pip install -r requirements.txt

# ----------------------------------------------------------------------------
# Stage 2 — frontend dependencies (installed from the lockfile)
# ----------------------------------------------------------------------------
FROM node:22-bookworm-slim AS frontend-deps
WORKDIR /build
COPY Frontend/package.json Frontend/package-lock.json ./
# Install scripts are skipped for the same reason as Frontend/Dockerfile: the
# optional native profiler in the New Relic agent would try to compile.
RUN npm ci --ignore-scripts --no-audit --no-fund

# ----------------------------------------------------------------------------
# Stage 3 — New Relic agent runtime for the web tier
#
# The agent is loaded through Node's own resolver (see
# src/lib/server/newrelic-agent.ts), so the bundler never traces it into the
# standalone output. This stage produces exactly the agent and its dependency
# closure for runtime. The version is read from package.json.
# ----------------------------------------------------------------------------
FROM node:22-bookworm-slim AS agent-deps
WORKDIR /agent
COPY Frontend/package.json ./
RUN node -e "const fs=require('node:fs');const pkg=JSON.parse(fs.readFileSync('package.json','utf8'));fs.writeFileSync('package.json',JSON.stringify({name:'documind-newrelic-agent',version:'1.0.0',private:true,dependencies:{newrelic:pkg.dependencies.newrelic}},null,2));" \
 && npm install --omit=dev --ignore-scripts --no-audit --no-fund \
 && rm -f package.json

# ----------------------------------------------------------------------------
# Stage 4 — frontend build (Next.js standalone output)
#
# Only NEXT_PUBLIC_* values are baked in here; server-only values are
# supplied at runtime. Build args can be overridden with --build-arg.
# ----------------------------------------------------------------------------
FROM node:22-bookworm-slim AS frontend-build
WORKDIR /build
ENV NEXT_TELEMETRY_DISABLED=1

ARG NEXT_PUBLIC_API_BASE_URL=/api/backend
ARG NEXT_PUBLIC_APPWRITE_ENDPOINT=
ARG NEXT_PUBLIC_APPWRITE_PROJECT_ID=
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL} \
    NEXT_PUBLIC_APPWRITE_ENDPOINT=${NEXT_PUBLIC_APPWRITE_ENDPOINT} \
    NEXT_PUBLIC_APPWRITE_PROJECT_ID=${NEXT_PUBLIC_APPWRITE_PROJECT_ID}

COPY --from=frontend-deps /build/node_modules ./node_modules
COPY Frontend/ ./
RUN npm run build

# ----------------------------------------------------------------------------
# Stage 5 — runtime
#
# Debian slim base matching the Python build (glibc), with the Node binary
# copied from the official Node image. Runs as an unprivileged user.
# ----------------------------------------------------------------------------
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    NEW_RELIC_CONFIG_FILE=/app/backend/newrelic.ini \
    NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    HOSTNAME=0.0.0.0 \
    PORT=10000 \
    BACKEND_URL=http://127.0.0.1:8000 \
    NEW_RELIC_LOG=stdout

# libstdc++/libgomp: compiled Chroma/ONNX extensions. supervisor: runs the three
# processes in one container. curl enables Heroku's release-phase log streaming.
RUN apt-get update \
 && apt-get install -y --no-install-recommends libstdc++6 libgomp1 supervisor curl \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --system --gid 1001 app \
 && useradd --system --uid 1001 --gid app --home-dir /app app

# Node.js runtime for the standalone Next.js server (copied, not installed).
COPY --from=node:22-bookworm-slim /usr/local/bin/node /usr/local/bin/node
# Python environment (API, worker, Alembic).
COPY --from=backend-deps /opt/venv /opt/venv

# Backend application, schema migrations and New Relic config.
COPY --chown=app:app Backend/app /app/backend/app
COPY --chown=app:app Backend/migrations /app/backend/migrations
COPY --chown=app:app Backend/alembic.ini Backend/newrelic.ini /app/backend/
# The backend entrypoint wraps a command in `newrelic-admin run-program` when
# NEW_RELIC_LICENSE_KEY is set; it is a no-op otherwise.
COPY --chown=app:app Backend/docker-entrypoint.sh /usr/local/bin/nr-entrypoint.sh
RUN sed -i 's/\r$//' /usr/local/bin/nr-entrypoint.sh \
 && chmod +x /usr/local/bin/nr-entrypoint.sh

# Frontend standalone server and its assets.
COPY --from=frontend-build --chown=app:app /build/.next/standalone /app/frontend
COPY --from=frontend-build --chown=app:app /build/.next/static /app/frontend/.next/static
COPY --from=frontend-build --chown=app:app /build/public /app/frontend/public
COPY --from=agent-deps --chown=app:app /agent/node_modules /app/frontend/node_modules
COPY --chown=app:app Frontend/newrelic.cjs /app/frontend/newrelic.cjs

# Supervisor program definitions: API on 127.0.0.1:8000 (internal), the PDF
# worker, and the web server on 0.0.0.0:${PORT} (the only public port).
# New Relic is enabled per process when NEW_RELIC_LICENSE_KEY is set.
# COPY works with hosted Docker builders without BuildKit heredoc support.
COPY Backend/deploy/supervisord.conf /etc/supervisor/documind.conf
COPY Backend/deploy/start-all-in-one.sh /usr/local/bin/start.sh
RUN sed -i 's/\r$//' /usr/local/bin/start.sh /etc/supervisor/documind.conf \
 && chmod +x /usr/local/bin/start.sh \
 && chown -R app:app /app

USER app
EXPOSE 10000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD ["python", "-c", "import os,sys,urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:%s/sign-in' % os.environ.get('PORT','10000'), timeout=5).status == 200 else 1)"]

CMD ["/usr/local/bin/start.sh"]
