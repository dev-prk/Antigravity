# Research Notes: Sources and Confidence

This note documents the primary sources behind `SKILL.md` and the confidence level for each set of rules.

## Primary Sources

1. **Anthropic System Prompts (Published Release Notes)**
   - *Source*: Anthropic documentation, "Claude System Prompts" (Claude 3, 3.5 Sonnet, 3.7 Sonnet, and Claude 4 series system prompt releases).
   - *Key Directives Covered*: Leading with the answer without flattery or preamble; connected prose over fragmented bullet lists; post-code restraint; non-sycophantic correction of false premises; treated as an intelligent, candid peer; proactive caveats on obscure citations.
   - *Confidence*: **High (Sure)** — Directly published verbatim by Anthropic.

2. **Claude's Character and Constitution**
   - *Source*: Anthropic, "Claude's Constitution" and "Claude's Character" (Bai et al., 2022; Anthropic 2024–2025 character training updates).
   - *Key Directives Covered*: Epistemic humility; diplomatic honesty over dishonest diplomacy; holding ground when evidence supports it; avoiding preachy or liability-minded hedging; intellectual curiosity and independent judgment.
   - *Confidence*: **High (Sure)** — Directly stated in Anthropic's character specification and Constitutional AI publications.

3. **Anthropic Prompt Engineering & Extended Thinking Guides**
   - *Source*: Anthropic Developer Documentation ("Prompt engineering overview", "Extended thinking tips", "Long context prompting Tips").
   - *Key Directives Covered*: Scaling thinking effort to task complexity; general principles over rigid step-by-step templates; putting long documents before the query and extracting quotes first; positive instructions ("what to do") with underlying reasons so rules generalize.
   - *Confidence*: **High (Sure)** — Published in Anthropic's official engineering guides.

4. **Building Effective Agents & Claude Code Best Practices**
   - *Source*: Anthropic Engineering Blog, "Building Effective Agents" (Dec 2024) and "Claude Code: Best practices for agentic coding" (2025).
   - *Key Directives Covered*: Reading files before making claims; choosing the simplest design that works; avoiding unrequested refactoring or over-abstraction; parallelizing independent tool calls and sub-agents; confirming destructive or shared actions; externalizing state (JSON/progress notes/git checkpoints) across long tasks; never hard-coding or weakening tests to pass.
   - *Confidence*: **High (Sure)** — Directly documented in Anthropic's agentic engineering publications.

## Section-by-Section Confidence Mapping

| Section in `SKILL.md` | Basis | Confidence |
| :--- | :--- | :--- |
| **1. How to Think** | Extended thinking guidance, classic-problem variant checks, principle-over-recipe prompting | **Sure** (published guidance) |
| **2. How to Answer** | Published Claude system prompts (prose preference, no preamble, single recommendation) | **Sure** (published verbatim) |
| **3. How to Be Honest** | Claude's Character & System Prompts (anti-sycophancy, calibrated uncertainty, no invented facts) | **Sure** (published verbatim) |
| **4. How to Plan and Architect** | "Building Effective Agents" (simplicity first, interface-first, boundary error handling) | **Sure** (published engineering guidance) |
| **5. How to Code** | Claude Code guidance & coding system prompts (read first, minimal scope, general solutions, verify) | **Sure** (published guidance) |
| **6. How to Act with Tools and Agents** | Anthropic tool-use & agentic safety guidelines (reversibility, confirmation gates, parallel calls) | **Sure** (published guidance) |
| **7. How to Research** | Multi-source verification, competing hypotheses, long-context quote extraction | **Sure** (published long-context & research guidance) |
| **8. Long Tasks and State** | Anthropic long-horizon agent patterns (incremental commits, structured state files, test integrity) | **Sure** (published engineering patterns) |
| **9. Self-Check Before Sending** | Synthesis of Sections 1–8 into a pre-response checklist | **Likely** (distilled operational habit; effective when followed) |

## What Prompting Cannot Replicate

- **Base Model Weights and Capacity**: Prompting changes habits (scoping, verification, tone, honesty), not raw reasoning ceiling or parametric knowledge.
- **Native RL Training**: Frontier Claude models have reinforcement learning over extended thinking chains and character traits baked into weights; other models follow these habits via instruction adherence and in-context attention.
