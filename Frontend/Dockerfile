# syntax=docker/dockerfile:1.7

# ---------------------------------------------------------------------------
# Stage 1 - dependencies
#
# Installed from the lockfile only, so the layer is reused whenever
# application source changes but the dependency graph does not.
# ---------------------------------------------------------------------------
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
# Install scripts are skipped: the optional native profiler shipped with the
# New Relic agent would try to compile, and nothing in this application needs
# a postinstall step.
RUN npm ci --ignore-scripts --no-audit --no-fund

# ---------------------------------------------------------------------------
# Stage 2 - New Relic agent runtime
#
# The agent is loaded through Node's own resolver (see
# src/lib/server/newrelic-agent.ts), so the bundler never traces it into the
# standalone output and the standalone image does not contain it. This stage
# produces the agent and the exact dependency closure it needs at runtime,
# and nothing else. The version is read from package.json so it can never
# drift.
# ---------------------------------------------------------------------------
FROM node:22-alpine AS agent-deps
WORKDIR /agent
COPY package.json ./
RUN node -e "const fs=require('node:fs');const pkg=JSON.parse(fs.readFileSync('package.json','utf8'));fs.writeFileSync('package.json',JSON.stringify({name:'documind-newrelic-agent',version:'1.0.0',private:true,dependencies:{newrelic:pkg.dependencies.newrelic}},null,2));" \
 && npm install --omit=dev --ignore-scripts --no-audit --no-fund \
 && rm -f package.json

# ---------------------------------------------------------------------------
# Stage 3 - build
#
# Next.js emits the traced standalone server plus the static assets. Only
# NEXT_PUBLIC_* values are baked in here; every server-only secret is
# supplied at runtime.
# ---------------------------------------------------------------------------
FROM node:22-alpine AS builder
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1

ARG NEXT_PUBLIC_API_BASE_URL=/api/backend
ARG NEXT_PUBLIC_APPWRITE_ENDPOINT=
ARG NEXT_PUBLIC_APPWRITE_PROJECT_ID=
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL} \
    NEXT_PUBLIC_APPWRITE_ENDPOINT=${NEXT_PUBLIC_APPWRITE_ENDPOINT} \
    NEXT_PUBLIC_APPWRITE_PROJECT_ID=${NEXT_PUBLIC_APPWRITE_PROJECT_ID}

COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 4 - runtime
#
# Contains the traced server, the static assets, the public folder and the
# New Relic agent. Runs as an unprivileged user.
# ---------------------------------------------------------------------------
FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0 \
    NEW_RELIC_LOG=stdout

RUN addgroup -S -g 1001 nodejs && adduser -S -u 1001 -G nodejs nextjs

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=agent-deps --chown=nextjs:nodejs /agent/node_modules ./node_modules
COPY --chown=nextjs:nodejs newrelic.cjs ./newrelic.cjs

USER nextjs
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider "http://127.0.0.1:${PORT:-3000}/sign-in" || exit 1

CMD ["node", "server.js"]
