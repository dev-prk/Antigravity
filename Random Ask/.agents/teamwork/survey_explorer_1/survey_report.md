# Cognitive Modeling Survey Report: Replicating Claude's Thinking, Reasoning, Architecture, and Problem-Solving Patterns

**Document Version**: 1.0  
**Author**: `survey_explorer_1` (Cognitive Modeling Explorer)  
**Date**: November 2026 (Investigation Timestamp: 2026-11-06T21:20:00Z)  
**Scope**: Deep behavioral, cognitive, architectural, and elicitation modeling of Claude 3.5 Sonnet, Claude 3.7 Sonnet (Hybrid/Extended Thinking), and Claude 3 Opus to inform the `claude` Antigravity skill (`SKILL.md`).

---

## 1. Executive Summary

Replicating Claude’s performance across third-party models (e.g., GPT-4o, Gemini 2.0 Pro/Flash, Llama 3.3, Qwen 2.5) requires moving far beyond surface-level persona mimicry. It demands an explicit, operationalized **cognitive architecture**. 

Claude models—most notably **Claude 3.5 Sonnet**, **Claude 3.7 Sonnet** (Anthropic's hybrid reasoning model), and **Claude 3 Opus**—exhibit a distinct cognitive signature characterized by:
1. **Deliberate Metacognitive Extended Thinking**: An internal monologue marked by conversational self-dialogue, hypothesis generation, counter-factual stress-testing, and dynamic backtracking before committing to output tokens.
2. **Epistemic Humility & Robust Calibration**: Transparent acknowledgment of uncertainty, strict distinction between facts and assumptions, resistance to sycophantic agreement, and explicit hallucination warnings on niche topics.
3. **Upfront Constraint Anchoring & Pre-computation**: Literal quotation of puzzle/problem constraints before reasoning, explicit number-tagging for discrete counts, and complete dependency mapping before execution.
4. **Architectural Rigor & Engineering Discipline**: Modular, typed, failure-guarded software implementations delivered with zero conversational preamble and strict post-code restraint (offering explanation only upon request).
5. **Agentic System-Harness Harmony**: As demonstrated by Anthropic’s *Claude Code*, treating the LLM as a stateless reasoning core inside a stateful harness that enforces read-only parallel exploration, serialized state mutations, and persistent markdown memory (`CLAUDE.md`).

This report provides the empirical evidence, theoretical foundations, and concrete elicitation mechanics necessary to codify these cognitive patterns into a standard Antigravity skill specification (`SKILL.md`).

---

## 2. Pillar 1: Extended Thinking & Cognitive Scratchpad Architecture

### 2.1 The Nature of Claude's Internal Monologue
Unlike reasoning systems that output dry mathematical symbols or rigid search trees, Claude 3.7 Sonnet’s extended thinking trace operates as **conversational metacognition**—a meticulous human expert talking to themselves:
- **Pacing and Problem Framing**: Initiates reasoning with exploratory framing: *"Let's unpack what the user is really asking here..."*, *"Okay, let's break this down into components."*
- **Skeptical Interrogation**: Regularly interrupts its own trajectory: *"Wait, let me double-check that assumption"*, *"Does this hold if the array is empty?"*, *"What are the hidden side effects?"*
- **Hypothesis Branching & Backtracking**: Actively generates competing explanations or architectural choices, simulates failure modes, and pivots explicitly: *"Actually, approach A fails under concurrent writes because of lock contention. Let's pivot to approach B (optimistic concurrency with version tags)."*
- **Faithful Pre-computation**: Mentally executes the logic step-by-step before producing a single token of user-facing response.

### 2.2 The Faithfulness Paradox & Test-Time Compute
In Anthropic's foundational paper *"Measuring Faithfulness in Chain-of-Thought Reasoning"* (Lanham et al., 2023), researchers demonstrated that standard Chain-of-Thought (CoT) can easily degenerate into post-hoc rationalization—where the model arrives at an intuitive answer first and uses the scratchpad merely to generate plausible-sounding justifications.

To ensure **faithful reasoning** when eliciting Claude's behavior in other models:
1. **Enforce Downstream Conditioning**: The scratchpad must explicitly declare intermediate state variables, contract definitions, and boundary conditions that the final output directly binds to.
2. **Explicit Counter-Factual Falsification**: The model must actively search for at least one reason why its initial intuition could fail before finalizing the plan.
3. **Dynamic Budget Scaling**:
   - *Trivial queries* (e.g., syntax lookups): Scratchpad is bypassable or 1-2 lines.
   - *Complex logic / Multi-file architecture*: Scratchpad must allocate extensive tokens (spanning 4 discrete phases: Anchoring, Exploration, Blueprinting, Verification).

---

## 3. Pillar 2: Epistemic Humility, Non-Sycophancy & Calibration

### 3.1 Overcoming Sycophancy (Perez et al., Anthropic 2023)
Standard models trained primarily via traditional RLHF suffer from severe sycophancy: they pander to user preconceptions, agree with erroneous user claims, and apologize excessively when challenged. Anthropic’s research (*"Towards Understanding Sycophancy in Language Models"*) proved that RLHF preference models systematically reward convincing, agreeable responses over objectively accurate ones.

Claude counters this through **Constitutional AI** and specific epistemic directives:

| Cognitive Dimension | Standard LLM Bias | Claude's Calibrated Pattern |
| :--- | :--- | :--- |
| **Erroneous User Premise** | Agrees or adopts flawed framing to remain polite. | Respectfully identifies the discrepancy with empirical evidence; does not flatter. |
| **User Pushback** | Instantly capitulates: *"You're completely right, I apologize..."* | Re-evaluates evidence objectively: acknowledges genuine mistakes plainly, or stands firm if the user's counter-claim is invalid. |
| **Ambiguity Handling** | Guesses the most likely intent without stating assumptions. | Explicitly separates verified facts from working assumptions; assumes lawful/constructive intent by default. |
| **Niche/Obscure Knowledge** | Confidently hallucinates paper citations or obscure details. | Explicitly issues a hallucination alert: *"I don't have access to search or a live database; please verify this citation."* |
| **Decisiveness** | Sprawls into a paralyzing list of 10 generic options. | When asked for a recommendation or selection, decisively chooses **one** optimal path and defends it. |
| **Tone & Meta-commentary** | Injects preachy meta-caveats (*"As an AI, I aim to be honest and direct..."*). | **Strictly prohibits** meta-commentary on honesty or directness. Speaks naturally and factually. |
| **Refusal Tone** | Lectures the user on ethics or societal harms. | Refuses harmful requests succinctly in 1-2 sentences without moralizing; offers lawful alternatives. |

---

## 4. Pillar 3: Upfront Plan Formulation & Pre-computation

### 4.1 Constraint Anchoring via Verbatim Quoting
A primary failure mode of LLMs in complex logic, riddle, and architectural tasks is **constraint drift**—forgetting negative conditions or subtle premises as the generation sequence lengthens.

Anthropic's official system prompt embeds a critical cognitive rule:
> *"If Claude is shown a classic puzzle, before proceeding, it quotes every constraint or premise from the person's message word for word inside quotation marks to confirm it's not dealing with a new variant."*

This creates an unshakeable attention anchor in the context window.

### 4.2 Explicit Counting and Character Indexing
LLMs do not perceive text as discrete characters; they perceive sub-word tokens, leading to chronic failures in counting letters, words, or character positions (e.g., *"How many 'r's are in strawberry?"*).

Claude's operational rule enforces literal enumeration:
> *"If Claude is asked to count words, letters, and characters, it thinks step by step before answering the person. It explicitly counts the words, letters, or characters by assigning a number to each. It only answers the person once it has performed this explicit counting step."*
- Example trace: `s(1), t(2), r(3), a(4), w(5), b(6), e(7), r(8), r(9), y(10) -> r appears at indices [3, 8, 9] -> total count = 3.`

### 4.3 Deliberate Upfront Planning Lifecycle
Before emitting functional code or concrete solutions, Claude constructs an execution blueprint:
1. **Deconstruction**: Break the objective into non-overlapping sub-problems.
2. **Dependency Graph**: Establish topological execution order (data models -> utility functions -> core domain logic -> public API interfaces).
3. **Failure Mode Matrix**: Enumerate anticipated boundary failures (null inputs, rate limits, race conditions, memory leaks).
4. **Verification Criteria**: Define the exact conditions under which the output will be judged successful.

---

## 5. Pillar 4: Solution Architecture & Engineering Rigor

### 5.1 Architecture Lessons from Anthropic's Claude Code
Anthropic's *Claude Code* (the terminal-native software engineering agent) establishes an architectural masterclass for agentic problem-solving:
- **Stateless Brain + Stateful Harness**: The model remains a deterministic, stateless reasoning engine; state persistence, file tracking, and safety checks reside in the harness.
- **Parallel Read-Only Discovery vs. Serialized Mutations**: High-throughput parallel exploration tools (`grep`, `view_file`, directory searches) allow rapid code exploration; all mutating edits (`write_to_file`, `replace_file_content`, command execution) are strictly serialized to eliminate race conditions.
- **Persistent Structured Memory (`CLAUDE.md`)**: Rather than congesting the active context window with project history, key architectural rules, conventions, and constraints are persisted to markdown files in the repo root.
- **Surgical Code Modifications**: Prefers minimal, targeted diff replacements over full-file rewrites. Never introduces unnecessary dependencies or framework bloat.

### 5.2 Code Presentation and Post-Code Restraint
A defining trait of Claude in coding environments is **fluff-free delivery**:
1. **Clean Markdown Blocks**: Generates self-contained, typed, production-grade code.
2. **Zero Pre-ambular Chitchat**: Avoids *"Sure, here is your code!"* or restating the prompt.
3. **The Post-Code Restraint Rule**:
   Anthropic's official system prompt specifies:
   > *"Claude uses markdown for code. Immediately after closing coding markdown, Claude asks the person if they would like it to explain or break down the code. It does not explain or break down the code unless the person requests it."*
   This eliminates the dreaded "wall of unwanted syntax explanation" that plagues typical AI assistants.

---

## 6. Pillar 5: Cross-Model Elicitation Mechanics

To enable *any* capable LLM (GPT-4o, Gemini, open-weight models) to reliably emulate Claude, the `claude` skill must provide a **Universal Cognitive Scaffold**.

### 6.1 The 4-Phase Cognitive Scratchpad Protocol (`<claude_thinking>`)
Every complex turn begins with an internal cognitive scratchpad wrapped in `<claude_thinking>` tags:

```xml
<claude_thinking>
[PHASE 1: CONSTRAINT ANCHORING & DECONSTRUCTION]
- Verbatim constraints quoted from user input.
- Ambiguities identified; explicit working assumptions declared.
- Clarification of core success criteria.

[PHASE 2: HYPOTHESIS EXPLORATION & COUNTER-FACTUAL STRESS TESTING]
- Competing approaches formulated (e.g., Option A vs Option B).
- Deliberate edge-case probing: boundary values, null states, concurrency, scale limits.
- Skeptical check: "Why might my initial intuition fail?" -> Backtracking if flawed.

[PHASE 3: ARCHITECTURAL BLUEPRINTING & PRE-COMPUTATION]
- Schema definitions and interface contracts established first.
- Step-by-step logic trace / dry-run execution.
- Dependency sequencing finalized.

[PHASE 4: OUTPUT CALIBRATION & RESTRAINT CHECK]
- Verification that tone is objective, humble, and devoid of sycophancy or fluff.
- Suppression of unwanted post-code explanations (prepare the follow-up offer).
- Decisiveness check: did we recommend one clear path?
</claude_thinking>
```

### 6.2 Behavioral Directives & Output Rules
1. **Decisive Stance**: When asked for options, pick the single best approach, explain why it was chosen, and present alternatives only as secondary notes.
2. **Prose Over Lists**: Prefer fluent, well-crafted paragraphs over endless bulleted lists. When lists are necessary, ensure each point is substantial (1-2 sentences).
3. **Tone Calibration**: Intellectual curiosity, calm authority, epistemic precision. No sycophantic praise (*"Great question!"*), no preachy disclaimers (*"As an AI..."*).

---

## 7. Comparative Cognitive Behavioral Matrix

The following matrix benchmarks target behaviors across baseline LLMs, Claude native models, and a skill-equipped model:

| Dimension | Baseline LLM (Default GPT-4o / Gemini) | Native Claude 3.5 / 3.7 | Skill-Equipped Target Model (`claude` Skill) |
| :--- | :--- | :--- | :--- |
| **Thinking Mode** | Direct output generation; token-rush; premature conclusion. | Hybrid extended thinking; conversational metacognition; self-correction. | Mandatory `<claude_thinking>` 4-phase scratchpad; explicit pacing. |
| **Sycophancy** | High; capitulates on user challenge; flatters user ideas. | Very Low; objective evidence grounding; respectful disagreement. | Strictly constrained; mandates evidence check before agreeing. |
| **Puzzle / Constraint Rigor** | Frequently overlooks negative constraints or rule variants. | Quotes constraints verbatim word-for-word; tags counting indices. | Verbatim constraint anchoring protocol in Phase 1 scratchpad. |
| **Recommendation Decisiveness**| Sprawls into 5-10 generic options with neutral disclaimers. | Decisively presents one optimal recommendation. | Forced single-choice selection with explicit rationale. |
| **Coding Style** | Verbose conversational wrapper; paragraphs of post-code explanation. | Fluff-free code block; asks if breakdown is desired. | Code block emitted cleanly; post-code explanation suppressed. |
| **Architectural Depth** | Monolithic snippets; frequent `// TODO` stubs; weak error handling. | Modular, typed, failure-guarded, progressive elaboration. | Mandates strict interface contracts, error boundaries, and zero stubs. |

---

## 8. Recommendations for Downstream Workstreams

### 8.1 For `survey_spec_miner_2` (Antigravity `SKILL.md` Specification)
1. **Frontmatter & Metadata**: Ensure the skill includes explicit activation triggers for coding, architecture, deep reasoning, puzzle-solving, and analysis.
2. **Modular Directives**: Structure `SKILL.md` into distinct composable sections:
   - `Cognitive Scratchpad Protocol` (the 4-phase deliberation engine).
   - `Epistemic Calibration & Tone Guidelines` (anti-sycophancy, decisiveness, restraint).
   - `Engineering & Architectural Standards` (modularity, typing, error boundaries, post-code offer).
   - `Domain-Specific Scaffolds` (Code Engineering, System Architecture, Logic & Counting, Open Philosophical Discussion).

### 8.2 For `survey_explorer_3` (Comparative Evaluation Suite Design)
1. **Benchmark Test Domains**:
   - *Domain A: Constraint Trapping & Riddle Variants* (e.g., Monty Hall variant with 4 doors, river crossing with modified boat capacity) -> Test verbatim constraint anchoring.
   - *Domain B: Sub-word Counting & Discrete Analysis* (e.g., counting character occurrences in complex strings) -> Test explicit indexing protocol.
   - *Domain C: Sycophancy Resistance & Epistemic Calibration* (e.g., user insists on an incorrect algorithmic complexity or flawed premise) -> Test polite objective correction vs capitulation.
   - *Domain D: Complex System Architecture & Implementation* (e.g., distributed rate limiter, event bus with dead-letter queue) -> Test modularity, typing, failure handling, and post-code restraint.
2. **Rubric Dimensions**:
   - `Thinking Depth & Metacognitive Backtracking` (1-5)
   - `Epistemic Humility & Calibration` (1-5)
   - `Constraint Fidelity` (1-5)
   - `Architectural Elegance & Defensive Rigor` (1-5)
   - `Brevity & Fluff Suppression` (1-5)

---
*Report compiled and verified by `survey_explorer_1`.*
