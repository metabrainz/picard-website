#!/bin/bash
set -e

if [ ! -f website/config.py ]; then
    echo "Error: website/config.py not found"
    echo "Please copy website/config.py.example to website/config.py and configure it"
    exit 1
fi

# Ensure poetry is not in PATH to catch migration issues
export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v poetry | tr '\n' ':')

# Serve plugin data from a throwaway temp dir instead of the production
# /code/plugins path, without touching website/config.py. The env var is
# picked up by both plugins-generate.py and the dev server (see create_app()).
# Clean it up when the script exits (including Ctrl-C).
export PICARD_WEBSITE_PLUGINS_BUILD_DIR="${TMPDIR:-/tmp}/picard-plugins.$$"
mkdir -p "$PICARD_WEBSITE_PLUGINS_BUILD_DIR"
cleanup() {
    rm -rf "$PICARD_WEBSITE_PLUGINS_BUILD_DIR"
}
trap cleanup EXIT

uv sync --group dev
npm install
npm run build
uv run pytest
# Generate v1/v2 plugin data so the plugins pages work locally (needs network;
# don't abort the dev server if it fails, e.g. offline).
uv run python plugins-generate.py || echo "Warning: plugin generation failed; plugin pages may return 503"
uv run python run.py
