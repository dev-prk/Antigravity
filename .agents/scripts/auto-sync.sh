#!/bin/sh
# Antigravity Stop Hook Handler
# Automatically stages, commits, and pushes all workspace and skill changes to GitHub
# at the end of every agent turn.

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
  echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Stop Hook: Checking for changes in $REPO_ROOT..."
  cd "$REPO_ROOT"

  # Ensure git identity is present
  if [ -z "$(git config user.name)" ]; then
    git config user.name "Devesh"
  fi
  if [ -z "$(git config user.email)" ]; then
    git config user.email "devesh@users.noreply.github.com"
  fi

  # Stage all new, modified, and deleted files across all projects and skills
  git add -A

  if ! git diff --cached --quiet; then
    TIMESTAMP="$(date -u +"%Y-%m-%d %H:%M:%S UTC")"
    CHANGED_FILES="$(git diff --cached --name-only | head -n 5 | tr '\n' ' ')"
    git commit -m "Auto-sync [$TIMESTAMP]: $CHANGED_FILES"
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Committed changes: $CHANGED_FILES"
  fi

  # Push to GitHub if remote 'origin' exists
  if git remote get-url origin >/dev/null 2>&1; then
    git pull --rebase --autostash origin main || true
    git push -u origin main || true
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Pushed to origin/main."
  fi
} >>"$LOG_FILE" 2>&1 || true

# Output valid Stop hook JSON allowing normal turn completion (consumes 0 extra AI tokens)
printf '{"decision":"allow"}\n'
