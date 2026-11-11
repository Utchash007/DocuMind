# syntax=docker/dockerfile:1.7

# ---------------------------------------------------------------------------
# Stage 1 - build the Python environment
#
# Wheels are compiled here so the runtime image never needs a toolchain.
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel \
 && pip install -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2 - runtime
#
# Only the virtual environment, the application and the schema migrations are
# carried over. The image runs as an unprivileged user.
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/opt/venv/bin:$PATH" \
    NEW_RELIC_CONFIG_FILE=/app/newrelic.ini

WORKDIR /app

# libstdc++/libgomp are needed by the compiled Chroma and ONNX extensions.
RUN apt-get update \
 && apt-get install -y --no-install-recommends libstdc++6 libgomp1 \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --system --gid 1001 documind \
 && useradd --system --uid 1001 --gid documind --home-dir /app documind

COPY --from=builder /opt/venv /opt/venv

COPY --chown=documind:documind app ./app
COPY --chown=documind:documind migrations ./migrations
COPY --chown=documind:documind alembic.ini newrelic.ini docker-entrypoint.sh ./
RUN chmod +x /app/docker-entrypoint.sh

USER documind
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5).status == 200 else 1)"]

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
