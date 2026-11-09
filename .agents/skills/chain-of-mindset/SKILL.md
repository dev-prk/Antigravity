---
name: chain-of-mindset
description: >-
  ONLY invoke when explicitly called by the user (e.g., /chain-of-mindset); never activate by default. Step-level adaptive cognitive mode switching (Chain-of-Mindset / CoM, arXiv:2602.10063) that dynamically orchestrates four heterogeneous mindsets—Algorithmic, Spatial, Divergent, and Convergent—via a Meta-Cognitive Orchestrator and Bidirectional Context Gate.
disable-model-invocation: true
disable-slash-command: false
license: MIT
---

# Chain of Mindset (CoM): Reasoning with Adaptive Cognitive Modes

Based on [QuantaAlpha/chain-of-mindset](https://github.com/QuantaAlpha/chain-of-mindset) (*Chain of Mindset: Reasoning with Adaptive Cognitive Modes*, arXiv:2602.10063).

Instead of applying a single fixed reasoning mode across an entire task, you act as a **Meta-Cognitive Orchestrator** that dynamically switches between four distinct cognitive mindsets as the problem state evolves, mediated by a **Bidirectional Context Gate**.

---

## 1. The Four Heterogeneous Mindsets

| Mindset | Trigger Tag | Cognitive Shift | When to Use |
| :--- | :--- | :--- | :--- |
| **Algorithmic** | `<call_algorithmic>` | Estimation $\to$ Precise Verification | A calculation, simulation, data check, or hypothesis needs objective verification via executable code (Generate $\to$ Execute $\to$ Fix $\to$ Retry). |
| **Spatial** | `<call_spatial>` | Verbal $\to$ Visual-Spatial Representation | Problem has geometric, structural, topological, or layout relationships that benefit from visual sketching, diagrams, or plotting. |
| **Divergent** | `<call_divergent>` | Single Path $\to$ Parallel Exploration | Uncertain which approach is right, or current approach is tedious/stuck; generate 2–5 genuinely different methods in parallel branches. |
| **Convergent** | `<call_convergent>` | Scattered $\to$ Deep Focused Analysis | Need to reason rigorously step-by-step down one specific logical thread grounded in established facts. |

---

## 2. Meta-Cognitive Orchestration Protocol

You decide **HOW** to think at each step before executing that thinking. Never solve the problem inside `<cognitive_decision>`—only diagnose the current state and plan which mindset(s) to invoke next.

1. **Plan / Re-plan (`<cognitive_decision>`)**:
   Identify the current problem state and select the sequence of mindsets. Revise the plan anytime a step reveals a simpler path or hits a wall.
2. **Input Context Gate (Filter Before Mindset Execution)**:
   Pass only what the chosen mindset needs:
   - *Keep verbatim*: numbers, constraints, coordinates, prior verified results.
   - *Summarize*: prior reasoning chains into conclusions only.
   - *Omit*: irrelevant history so the mindset focuses strictly on its sub-task.
3. **Execute Mindset (`<call_xxx>` $\to$ `<xxx_result>`)**:
   - **Divergent**: Generate `<branch id="A">`, `<branch id="B">`, etc., with distinct methods, assumptions, and limitations.
   - **Convergent**: Focus all attention on the single sub-question; ground each step in established facts; state what is missing if insufficient.
   - **Algorithmic**: Write and run Python code (or trace deterministically if no shell is available) to compute or verify the exact result.
   - **Spatial**: Construct an explicit visual/structural representation (ASCII/Mermaid diagram, coordinate map, or matplotlib plot via `./scripts/`).
4. **Output Context Gate & Internalization (`<insight>`)**:
   Distill the mindset output into computed values, discovered patterns, or conclusions (omitting failed intermediate derivations) inside a brief `<insight>...</insight>` block.
5. **Final Synthesis (`<Answer>`)**:
   Once verified, present the final response clearly.

---

## 3. Canonical Execution Trace

```text
<cognitive_decision>
Pursuit problem with oscillation. Convergent -> Algorithmic.
</cognitive_decision>

<call_convergent>Model the bee's path between the two approaching trains.</call_convergent>
<convergent_result>Infinite series: sum each segment as the bee bounces back and forth.</convergent_result>
<insight>Series approach works in principle, but summing infinite segments is tedious. Re-plan.</insight>

<cognitive_decision>
Method too complex. Switch to Divergent -> Algorithmic.
</cognitive_decision>

<call_divergent>Find alternative formulations for total distance flown.</call_divergent>
<divergent_result>
- Branch A: Sum infinite geometric series of bounce segments.
- Branch B: Total flight time equals time until trains meet (d_total = v_bee * t_meet).
- Branch C: Transform to one train's reference frame.
</divergent_result>
<insight>Branch B bypasses the infinite series: just compute train meeting time.</insight>

<call_algorithmic>t_meet = 300 / (60 + 90) = 2 hours. d_bee = 120 * 2.</call_algorithmic>
<algorithmic_result>240 km.</algorithmic_result>
<insight>Verified exact answer: 240 km.</insight>
```

---

## 4. Standalone Python Runner (Included)

The complete upstream Python implementation of Chain-of-Mindset is bundled in [`./scripts/`](./scripts/):
- [`./scripts/main_api.py`](./scripts/main_api.py) — API mode entry point
- [`./scripts/main_local.py`](./scripts/main_local.py) — Local vLLM/Ollama entry point
- [`./scripts/main_without_spatial.py`](./scripts/main_without_spatial.py) — Text-only 3-mindset runner
- [`./scripts/core/orchestrator.py`](./scripts/core/orchestrator.py) & [`./scripts/core/gate.py`](./scripts/core/gate.py) — Meta-Agent & Bidirectional Context Gate
