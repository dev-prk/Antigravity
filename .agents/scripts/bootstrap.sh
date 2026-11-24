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
mkdir -p "$HOME/.local/bin"
chmod +x "$REPO_ROOT/.agents/scripts/freellm"
ln -sfn "$REPO_ROOT/.agents/scripts/freellm" "$HOME/.local/bin/freellm"

# 4b. Auto-wire FreeLLMAPI MCP server into ~/.gemini/config/mcp_config.json if FreeLLMAPI DB exists
FREELLM_DB="$HOME/Library/Application Support/FreeLLMAPI/freeapi.db"
if [ -f "$FREELLM_DB" ] && [ ! -f "$GLOBAL_CONFIG_DIR/mcp_config.json" ]; then
  FREE_KEY="$(sqlite3 -readonly "$FREELLM_DB" "SELECT value FROM settings WHERE key='unified_api_key'" 2>/dev/null || true)"
  if [ -n "$FREE_KEY" ]; then
    cat > "$GLOBAL_CONFIG_DIR/mcp_config.json" <<EOF
{
  "mcpServers": {
    "freellmapi": {
      "serverUrl": "http://127.0.0.1:31415/mcp",
      "headers": {
        "Authorization": "$FREE_KEY"
      }
    }
  }
}
EOF
  fi
fi

# 5. If remote 'origin' is configured, pull latest state from GitHub
if git remote get-url origin >/dev/null 2>&1; then
  git pull --rebase --autostash origin main >/dev/null 2>&1 || true
fi
