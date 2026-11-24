# Devesh's Antigravity Rules

## 1. Operating Standard (always on, every model, every project)

These rules come from a review of 200+ past chats in which work failed, was called "garbage", got cut off, or needed many retries. Follow them on every task, whether or not a skill is invoked.

### Understand before building
- Restate the goal in one sentence and list the **acceptance criteria**: what the user will look at to decide it's done. For anything bigger than a small edit, put them at the top of the plan.
- Before building, ask: *"What would an expert in this field say is missing?"* Find the domain-critical inputs first. For example, an astrology app built without place of birth was rejected outright.
- Treat every specific in the user's message as a hard requirement ("3D not 2D", "natural kid-friendly voice", "PostgreSQL only", "no salary figures", "run in background"). Re-check each one before finishing.
- If a critical input or preference is missing and a wrong guess would be expensive, ask up to 3 short questions in one message. Otherwise state the assumption in one line and proceed.

### Do the work directly and simply
- **Use one agent by default.** Use subagents or /teamwork only for truly independent, parallel work, with at most 3 running at once. Past runs spawned 180+ subagents, used up the quota, and left tasks half-finished.
- If the user stacks skills (e.g. `/aios /teamwork /goal /chain-of-mindset`), choose one lead process and use the rest as guidance. Never run several protocols on top of each other.
- Never show internal rituals to the user (phase headers, "constraint anchoring", `<thinking>` blocks, quoting the prompt back). Think silently and show results.
- Build the simplest thing that meets the acceptance criteria. Add frameworks, ledgers, extra pipelines or hundreds of tests only when asked.

### Verify the way the user will
- Before saying "done", check the real output the way the user will experience it. Look at rendered frames, listen to the audio, open the page, ask the chatbot a real follow-up question, run the code on real input. Passing unit tests does not prove the product works.
- Finish with a check against every acceptance criterion and every explicit specific, marked done / not done / not verified. Never claim anything you didn't check.
- Never end a turn on "waiting for X to finish" or "I will update you" when the user isn't needed. Wait for the task, then report. If you must stop, say exactly what's finished, what isn't, and the next step.
- When the user rejects work, find the root cause, fix it, and re-verify the whole deliverable, not just the one symptom they mentioned.

### Respect the quota
- The user is on a limited plan. Read only what you need, don't re-read large files, keep replies short, and don't re-summarize artifacts.
- **Model priority (`FreeLLMAPI` first → `Gemini → Claude → GPT` on expiry):**
  - Antigravity's main UI turn runs on the selected cloud model, while worker tasks route through `~/.local/bin/freellm` (and the `freellmapi` MCP server at `127.0.0.1:31415`).
  - Offload self-contained volume work (summarizing big files/logs with `-f`/`-o`, drafting text/boilerplate/tests, independent math/diff checks) to `~/.local/bin/freellm -m <coder|reader|auditor|writer|polyglot|fast>` **first** so free models absorb token volume.
  - `freellm` tries `FreeLLMAPI` (`127.0.0.1:31415`) first, then the built-in keyless free pool, and **automatically falls back to `Gemini → Claude → GPT` (`agy`) only when all free models are expired/exhausted**. Always verify worker output before accepting it.
- For multi-step work, keep a short `PROGRESS.md` (goal, criteria, done, next) in the project folder. On "resume" or "continue", read it first and pick up from there without redoing work.

### Communicate plainly
- Lead with the result, in short, plain language. Say when you're unsure. If the user is wrong, say so politely and explain why.
- Never ask the user to paste passwords or secrets into chat. Ask them to log in themselves in the browser.

### Browser
- Reuse the existing browser session and open new tabs instead of launching new windows. If the user says they're using the browser, work in the background or headless.

---

## 2. Cloud Sync & Zero-Touch Laptop Reset

This repo (`git@github.com:dev-prk/Antigravity.git`) is the single source of truth for all projects, skills, rules and hooks.

- **Fresh laptop + repo link (even with no instructions):** clone to `~/Documents/Antigravity` if it isn't there, run `chmod +x ~/Documents/Antigravity/.agents/scripts/*.sh && ~/Documents/Antigravity/.agents/scripts/bootstrap.sh`, then confirm in one sentence that skills, rules and sync hooks are restored.
- **Projects** live in subfolders of `~/Documents/Antigravity/`, never only in `/tmp`, `~/Desktop` or untracked folders.
- **Skills** live in `~/Documents/Antigravity/.agents/skills/<name>/SKILL.md`, which is symlinked to `~/.gemini/config/skills/`.
- **Sync is automatic:** the SessionStart hook pulls and the Stop hook commits and pushes. Both are shell scripts that use no AI tokens. **Never run `.agents/scripts/auto-sync.sh` manually**, and never wait on a sync, unless the user asks.

## 3. Skill Invocation

- **Global skills** (`~/Documents/Antigravity/.agents/skills/`) run ONLY when the user calls them explicitly (`/<skill-name>` or by name). Every global `SKILL.md` must have `disable-model-invocation: true`, `disable-slash-command: false`, and a description that says `ONLY invoke when explicitly called by the user (e.g., /<skill-name>); never activate by default.`
- **Exception:** project skills in `Content Creation/.agents/skills/` activate automatically for content and video work inside `Content Creation/` (see `Content Creation/GEMINI.md`).
- Section 1 above is always on. A skill adds to it but never replaces it.
