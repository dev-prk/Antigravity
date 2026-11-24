---
name: freellm
description: >-
  ONLY invoke when explicitly called by the user (e.g., /freellm); never activate by default.
  Routes tasks through FreeLLMAPI free models first, automatically falling back to Gemini -> Claude -> GPT
  only when all free pools are expired or rate-limited.
disable-model-invocation: true
disable-slash-command: false
---

# FreeLLM Priority Router (`/freellm`)

Run work on FreeLLMAPI's free models first, and switch to paid/quota models (`Gemini -> Claude -> GPT`) **only** when the free pools are expired.

## 1. Check Pool Health First
Run:
```bash
~/.local/bin/freellm --status
```

## 2. Route Work Through `freellm`
Pass large inputs via `-f` and write long outputs via `-o` so they stay out of the main chat context:
```bash
# Roles: coder, reader, auditor, tester, writer, polyglot, fast, triage, vision
~/.local/bin/freellm -m coder -f input.py -o out.py "task"
~/.local/bin/freellm -m reader -f huge.log -o summary.md "Summarize errors and root causes"
```

### How Cascading Fallback Works Automatically
1. **Tier 1 (`tier1:freellmapi`):** Calls `http://127.0.0.1:31415/v1/messages` across the role's models and `auto` (uses Groq, NVIDIA, OpenRouter, OVH, or any healthy key in FreeLLMAPI).
2. **Tier 2 (`tier2:free-keyless`):** If Tier 1 returns `exhausted` / `429`, falls back to FreeLLMAPI's built-in keyless pool (`kilo-auto/free`, `openrouter/free`) at zero quota cost.
3. **Tier 3 (`tier3:fallback`):** Only if both free tiers are expired or down, falls back via `~/.gemini/bin/agy` in strict order: `Gemini -> Claude -> GPT` (unless `--free-only` is passed).

## 3. Audit Before Accepting
Free models can hallucinate or drift. Always run/check the output yourself (run the script, check edge cases, grep against forbidden terms) before reporting done.
