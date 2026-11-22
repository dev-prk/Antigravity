#!/bin/sh
set -e
cd "$(dirname "$0")"
echo "Starting AstroPalm on http://127.0.0.1:8780"
exec .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8780
