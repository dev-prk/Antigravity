---
name: aios
description: ONLY invoke when explicitly called by the user (e.g., /aios); never activate by default. AI-OS protocol for multi-step work with ledger, token budget and HANDOFF.md resume.
disable-model-invocation: true
disable-slash-command: false
---
# AI-OS protocol
1. Run `cd ~/Documents/Antigravity/AI-OS && python3 -m aios status` first. If a task is active, continue from its "Next action". Never restart done steps.
2. New task: classify it. Trivial = answer directly. Otherwise plan 3-10 steps and create the task: `python3 -m aios new "<goal>" <token_limit> "step1" "step2" ...`
3. Per step: do it, run a real check (test/command), then `python3 -m aios done <seq> "<evidence>"`. Never mark done without real output.
4. Stay inside the token limit. At 80% finish the current step, then stop. `HANDOFF.md` is rewritten on every `done`.
5. A different model should review critical work, or use a fresh context.
6. Policy: honour `config/policies.json`. Never touch files outside the workspace without approval. Never print secrets.
7. Report only verified results, with open risks.
Reuse skills `claude`, `orchestration`, `loop-engineering` for reasoning style; don't restate them.
