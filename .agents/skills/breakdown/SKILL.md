---
name: breakdown
description: ONLY invoke when explicitly called by the user (e.g., /breakdown); never activate by default. Turns an idea or change into goal, deadline, researched plan, and small checkpoints. Plans only, never builds.
disable-model-invocation: true
disable-slash-command: false
---

# Breakdown (Goal + Deadline + Plan + Small Action)

Plan only. Do not write code or build anything.

## Step 1: Goal and deadline
- Goal: 1 measurable sentence.
- Deadline: ask if missing. Max 3 questions total.
- Done looks like: a pass/fail test.

## Step 2: Decompose
- Split into 5-10 chunks, ordered by dependency, riskiest first.
- Always include: inputs, data sources, core logic, output/UI, testing, failure cases.

## Step 3: Research (internet)
- Run separate web searches per chunk for: standard method or library, common mistakes, trusted source to verify against.
- Prefer official docs over blogs.
- Max 8 searches total unless told otherwise.
- Record finding + source URL. Flag conflicts.

## Step 4: Checkpoints
For each: Task (under 1 hour), Done when, Verify against, Risks, Target date (back-calculated from deadline).
Mark STOP points needing user approval.

## Output
1. Goal + deadline
2. Checkpoint table with dates
3. Top 3 risks
4. Today's single first action

Keep it short. No filler.
