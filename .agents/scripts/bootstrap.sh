#!/bin/sh
# Antigravity Zero-Touch Bootstrap Script
# Restores all global skills, rules, and lifecycle hooks from this repository
# onto a freshly formatted laptop and pulls the latest state from GitHub.

set -e

# Resolve the real path of this script even if invoked via a symlink
SOURCE="$0"
while [ -h "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [ "${SOURCE#/}" = "$SOURCE" ] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
GLOBAL_CONFIG_DIR="$HOME/.gemini/config"

mkdir -p "$GLOBAL_CONFIG_DIR"

# 1. Ensure git identity is configured locally so automated commits never fail
cd "$REPO_ROOT"
if [ -z "$(git config user.name)" ]; then
  git config user.name "Devesh"
fi
if [ -z "$(git config user.email)" ]; then
  git config user.email "devesh@users.noreply.github.com"
fi

# 2. Symlink Global Skills (~/.gemini/config/skills -> <repo>/.agents/skills)
if [ -L "$GLOBAL_CONFIG_DIR/skills" ] || [ ! -e "$GLOBAL_CONFIG_DIR/skills" ]; then
  ln -sfn "$REPO_ROOT/.agents/skills" "$GLOBAL_CONFIG_DIR/skills"
elif [ -d "$GLOBAL_CONFIG_DIR/skills" ]; then
  cp -rn "$GLOBAL_CONFIG_DIR/skills/"* "$REPO_ROOT/.agents/skills/" 2>/dev/null || true
  rm -rf "$GLOBAL_CONFIG_DIR/skills"
  ln -sfn "$REPO_ROOT/.agents/skills" "$GLOBAL_CONFIG_DIR/skills"
fi

# 3. Symlink Global Rules (~/.gemini/config/GEMINI.md -> <repo>/GEMINI.md)
ln -sfn "$REPO_ROOT/GEMINI.md" "$GLOBAL_CONFIG_DIR/GEMINI.md"
ln -sfn "$REPO_ROOT/AGENTS.md" "$GLOBAL_CONFIG_DIR/AGENTS.md"

# 4. Symlink Global Hooks & Scripts so hooks work even outside the repo root
ln -sfn "$REPO_ROOT/.agents/hooks.json" "$GLOBAL_CONFIG_DIR/hooks.json"
ln -sfn "$REPO_ROOT/.agents/scripts" "$GLOBAL_CONFIG_DIR/scripts"

# 5. If remote 'origin' is configured, pull latest state from GitHub
if git remote get-url origin >/dev/null 2>&1; then
  git pull --rebase --autostash origin main >/dev/null 2>&1 || true
fi
