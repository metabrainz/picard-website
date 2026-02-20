#!/bin/bash
set -e

if [ ! -f website/config.py ]; then
    echo "Error: website/config.py not found"
    echo "Please copy website/config.py.example to website/config.py and configure it"
    exit 1
fi

uv sync --extra dev
npm install
npm run build
uv run pytest
uv run python run.py
