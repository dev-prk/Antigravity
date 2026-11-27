#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
echo "Starting CBSE Shorts on http://localhost:8770"
exec python3 -m http.server 8770
