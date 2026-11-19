#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  .venv/bin/pip install --upgrade pip
  .venv/bin/pip install -r requirements.txt
fi

export PYTHONPATH="$(pwd)"
echo "Starting AstroFluence Dual-Mode Server..."
echo "  -> Personal Workbench: http://127.0.0.1:8765/workbench"
echo "  -> Website Chatbot:    http://127.0.0.1:8765/chat"
exec .venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8765 --reload
