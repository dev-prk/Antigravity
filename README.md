# Antigravity Cloud Workspace

This private repository backs up and continuously syncs all of Devesh's Antigravity projects, skills (`/claude`), rules (`GEMINI.md`), and lifecycle hooks (`.agents/hooks.json`).

## After Formatting / Resetting Your Laptop

You do **not** need to configure or explain anything manually. Just open Antigravity and paste this repository's URL into the chat (or clone it and open it):

```text
https://github.com/dev-prk/Antigravity.git
```

The agent will read [`GEMINI.md`](./GEMINI.md) and automatically run [`.agents/scripts/bootstrap.sh`](./.agents/scripts/bootstrap.sh) to restore:
- All global and workspace skills (`.agents/skills/claude` $\to$ `~/.gemini/config/skills`)
- All global rules (`GEMINI.md` $\to$ `~/.gemini/config/GEMINI.md`)
- Continuous auto-sync hooks (`.agents/hooks.json` $\to$ `~/.gemini/config/hooks.json`)
- All project directories (`Random Ask/`, `Automation/`, etc.)

### Or Run One Command in Terminal:
```sh
git clone git@github.com:dev-prk/Antigravity.git ~/Documents/Antigravity && ~/Documents/Antigravity/.agents/scripts/bootstrap.sh
```
