# Antigravity Cloud-First Workspace & Zero-Touch Laptop Reset Protocol

This repository is the single source of truth for all of Devesh's Antigravity projects, custom skills, rules, and automation hooks. Nothing should ever remain trapped offline.

---

## 1. Zero-Explanation Laptop Reset Protocol (For Fresh Machines)

If the user gives you (the Antigravity agent) a link to this GitHub repository on a freshly formatted laptop—even with **zero additional instructions**—you **MUST** execute the following recovery sequence immediately and autonomously without asking unnecessary questions:

1. **Clone into the Standard Workspace Root (if not already cloned):**
   ```sh
   mkdir -p ~/Documents
   git clone <REPO_URL> ~/Documents/Antigravity
   ```
2. **Execute the Zero-Touch Bootstrap Script:**
   ```sh
   chmod +x ~/Documents/Antigravity/.agents/scripts/*.sh
   ~/Documents/Antigravity/.agents/scripts/bootstrap.sh
   ```
   Running `bootstrap.sh` automatically:
   - Restores all global skills (`~/.gemini/config/skills` $\to$ `~/Documents/Antigravity/.agents/skills`), including `/claude`.
   - Installs global rules (`~/.gemini/config/GEMINI.md` and `AGENTS.md`).
   - Activates global lifecycle hooks (`~/.gemini/config/hooks.json`) for automatic `SessionStart` pull and `Stop` auto-commit/push.
3. **Confirm Ready State:**
   Inform the user in one concise sentence that all projects, skills (`/claude`), and continuous GitHub auto-sync hooks are restored and active.

---

## 2. Continuous Online Sync Rules (Always Active)

1. **Where to Store Projects:**
   All projects live as subdirectories inside `~/Documents/Antigravity/` (e.g., `Random Ask/`, `Automation/`, or any new project folder). Never store project code solely in `/tmp`, `~/Desktop`, or untracked directories.
2. **Where to Store Skills & Rules:**
   All reusable skills MUST be stored in `~/Documents/Antigravity/.agents/skills/<skill-name>/SKILL.md` (which is symlinked to `~/.gemini/config/skills/`). Creating or updating a skill here makes it immediately available across all workspaces and pushes it to GitHub automatically.
3. **Explicit-Only Skill Invocation Rule (For Global Skills in `~/.gemini/config/skills/`):**
   - **Never Invoke Global Skills by Default**: Custom global skills in `~/.gemini/config/skills/` (`~/Documents/Antigravity/.agents/skills/`) MUST NEVER be activated automatically or by default based on general topic matching.
   - **Explicit Call Required for Global Skills**: Only activate or read a global skill when the user explicitly invokes it by slash command (e.g., `/claude`, `/fable-mindset`, `/orchestration`, `/loop-engineering`, `/chain-of-mindset`, `/universal-fable-5`, `/ponytail`, `/karpathy-guidelines`, `/founder-skill`, `/founder-board`, etc.) or explicitly names the skill in their prompt.
   - **Frontmatter Enforcement for Global Skills**: Every existing and newly created global `SKILL.md` in `~/Documents/Antigravity/.agents/skills/` MUST include `disable-model-invocation: true` and `disable-slash-command: false` in its YAML frontmatter, and its `description` must state `ONLY invoke when explicitly called by the user (e.g., /<skill-name>); never activate by default.`
   - **Project-Scoped Exception (`Content Creation/.agents/skills/`)**: Project-local skills stored inside `~/Documents/Antigravity/Content Creation/.agents/skills/` are scoped exclusively to the `Content Creation` workspace (`disable-model-invocation: false`) and **MUST automatically activate** whenever the user prompts for content creation, 2D/3D animation, character consistency, or voice/video production inside `Content Creation/`.
4. **Automated GitHub Sync (`hooks.json`):**
   - **On `SessionStart`**: `.agents/scripts/session-start.sh` automatically runs `bootstrap.sh` and `git pull --rebase --autostash origin main` so the workspace always starts with the latest online commits.
   - **On `Stop` (End of Every Turn)**: `.agents/scripts/auto-sync.sh` automatically stages all changes (`git add -A`), creates a timestamped commit, and pushes to `origin main`.
   - **Manual Verification**: Whenever you finish creating a major feature, skill, or project, verify that `.agents/scripts/auto-sync.sh` has cleanly committed and pushed all changes (`git status` should be clean).
