# Antigravity Cloud-First Workspace & Zero-Touch Laptop Reset Protocol

See [GEMINI.md](./GEMINI.md) for the complete Zero-Explanation Laptop Reset Protocol and Continuous Online Sync Rules.

## Immediate Agent Directive on Fresh Laptop Reset
If the user provides this repository URL on a freshly reset machine with no other instructions:
1. Clone this repository to `~/Documents/Antigravity` (if not already present).
2. Run `~/Documents/Antigravity/.agents/scripts/bootstrap.sh` to symlink `~/.gemini/config/skills`, `~/.gemini/config/GEMINI.md`, and `~/.gemini/config/hooks.json`.
3. Confirm that all skills (`/claude`, `/fable-mindset`, `/chain-of-mindset`, `/universal-fable-5`, `/ponytail`, `/karpathy-guidelines`, `/founder-skill`, etc.), projects (`Random Ask`, `Automation`), and continuous GitHub auto-sync hooks are live.

## Explicit-Only Skill Invocation Rule
Never activate any custom skill by default or via implicit topic matching. Only invoke a custom skill when the user explicitly calls it (e.g., `/<skill-name>` or by explicitly asking to use that named skill). Every custom `SKILL.md` must set `disable-model-invocation: true`.
