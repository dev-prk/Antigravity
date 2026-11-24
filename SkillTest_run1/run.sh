#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
PYTHON_BIN="/Users/devesh/Documents/Antigravity/AstroPalm/.venv/bin/python"
if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi
exec "$PYTHON_BIN" -m uvicorn app:app --host 127.0.0.1 --port 8765
