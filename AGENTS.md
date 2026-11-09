# Antigravity Cloud-First Workspace & Zero-Touch Laptop Reset Protocol

See [GEMINI.md](./GEMINI.md) for the complete Zero-Explanation Laptop Reset Protocol and Continuous Online Sync Rules.

## Immediate Agent Directive on Fresh Laptop Reset
If the user provides this repository URL on a freshly reset machine with no other instructions:
1. Clone this repository to `~/Documents/Antigravity` (if not already present).
2. Run `~/Documents/Antigravity/.agents/scripts/bootstrap.sh` to symlink `~/.gemini/config/skills`, `~/.gemini/config/GEMINI.md`, and `~/.gemini/config/hooks.json`.
3. Confirm that all skills (`/claude`, `/fable-mindset`, `/chain-of-mindset`, `/universal-fable-5`, `/ponytail`, `/karpathy-guidelines`, `/founder-skill`, etc.), projects (`Random Ask`, `Automation`), and continuous GitHub auto-sync hooks are live.

## Explicit-Only Global Skill Invocation Rule (With Project-Scoped Exception for `Content Creation`)
Never activate any global skill in `~/Documents/Antigravity/.agents/skills/` by default or via implicit topic matching—only invoke global skills when the user explicitly calls them (e.g., `/<skill-name>`).
**Exception:** Project-local skills inside `~/Documents/Antigravity/Content Creation/.agents/skills/` are scoped exclusively to the `Content Creation` project (`disable-model-invocation: false`) and automatically activate on user requests within `Content Creation/`. See [Content Creation/GEMINI.md](./Content%20Creation/GEMINI.md).
