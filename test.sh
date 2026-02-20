#!/bin/bash
set -e

if [ ! -f website/config.py ]; then
    echo "Error: website/config.py not found"
    echo "Please copy website/config.py.example to website/config.py and configure it"
    exit 1
fi

# Ensure poetry is not in PATH to catch migration issues
export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v poetry | tr '\n' ':')

uv sync --extra dev
npm install
npm run build
uv run pytest
uv run python run.py
