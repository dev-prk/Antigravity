#!/bin/sh
# Antigravity SessionStart Hook Handler
# Runs bootstrap.sh and pulls the latest commits from GitHub when a session starts.

# Consume stdin payload
cat >/dev/null 2>&1 || true

# Resolve script directory following symlinks
SOURCE="$0"
while [ -h "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [ "${SOURCE#/}" = "$SOURCE" ] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_FILE="$REPO_ROOT/.agents/sync.log"

{
  echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] SessionStart: Running bootstrap & git pull..."
  "$SCRIPT_DIR/bootstrap.sh"
} >>"$LOG_FILE" 2>&1 || true

if git -C "$REPO_ROOT" remote get-url origin >/dev/null 2>&1; then
  REMOTE_URL="$(git -C "$REPO_ROOT" remote get-url origin)"
  printf '{"injectSteps":[{"systemMessage":{"systemMessage":"[Cloud Sync Active] Workspace & skills synced with GitHub (%s). All changes auto-commit and push at the end of every turn."}}]}\n' "$REMOTE_URL"
else
  printf '{"injectSteps":[{"systemMessage":{"systemMessage":"[Cloud Sync Pending Remote] Local Git initialized and hooks installed, but GitHub remote origin is not yet set. Ask the user for their private GitHub repo URL to complete online sync."}}]}\n'
fi
