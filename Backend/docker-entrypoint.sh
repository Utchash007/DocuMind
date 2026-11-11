#!/bin/sh
# Container entrypoint for the DocuMind backend image.
#
# The same image runs the API, the PDF worker and one-off Alembic commands.
# When a New Relic license key is configured the command is started through
# `newrelic-admin run-program`, which loads the agent before the application
# code is imported. Without a license key the command is started unchanged, so
# local and test environments never depend on the agent.
set -eu

if [ -n "${NEW_RELIC_LICENSE_KEY:-}" ]; then
  exec newrelic-admin run-program "$@"
fi

exec "$@"
