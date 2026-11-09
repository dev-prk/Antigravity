# DISPATCH — 2026-11-06T22:35:00Z

## Assignment: Milestone 3 Suite Implementer (`m3_worker_1`)
- Agent: `m3_worker_1`
- Working Directory: `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m3_worker_1`
- Original Request: `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/ORIGINAL_REQUEST.md`
- Scope Document: `/Users/devesh/Documents/Antigravity/Random Ask/PROJECT.md`
- Behavioral Checklist Reference: `/Users/devesh/Documents/Antigravity/Random Ask/skills/claude/resources/behavioral_checklist.json`
- Prompt Scaffolds Reference: `/Users/devesh/Documents/Antigravity/Random Ask/skills/claude/resources/prompt_scaffolds.md`

## Input Explorer Blueprints
1. Schemas & Benchmark Dataset:
   - Analysis: `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m3_explorer_1/analysis.md`
   - Handoff: `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m3_explorer_1/handoff.md`
2. Scoring Engine & Metrics:
   - Analysis: `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m3_explorer_2/analysis.md`
   - Handoff: `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m3_explorer_2/handoff.md`
3. Evaluation Runner & Judge Architecture:
   - Analysis: `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m3_explorer_3/analysis.md`
   - Handoff: `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m3_explorer_3/handoff.md`

## Target Deliverables (Exclusive Write Ownership)
- `/Users/devesh/Documents/Antigravity/Random Ask/tests/evaluation/__init__.py`
- `/Users/devesh/Documents/Antigravity/Random Ask/tests/evaluation/schemas.py`
- `/Users/devesh/Documents/Antigravity/Random Ask/tests/evaluation/benchmarks.jsonl`
- `/Users/devesh/Documents/Antigravity/Random Ask/tests/evaluation/scoring.py`
- `/Users/devesh/Documents/Antigravity/Random Ask/tests/evaluation/judge.py`
- `/Users/devesh/Documents/Antigravity/Random Ask/tests/evaluation/runner.py`

## Instructions
1. Implement all 6 deliverable files under `tests/evaluation/` adhering strictly to the explorer designs and E2E test contracts.
2. Ensure `benchmarks.jsonl` contains exactly 15 valid JSON lines spanning all 5 dimensions (`TC-CR-01` to `TC-EH-03`).
3. Ensure `scoring.py` implements CCRS, BCR (12 markers), IDS, and bootstrap statistics.
4. Ensure `judge.py` implements structured anti-verbosity prompt, 1-3-5 rubric evaluation, and dual-run position-swapping.
5. Ensure `runner.py` provides complete CLI with `--benchmarks`, `--output`, `--condition`, `--mock`, etc., and includes a rich offline `MockModelProvider` for automated testing.
6. Run tests:
   - `python3 -m pytest -m m3 tests/e2e/ -v`
   - `python3 tests/evaluation/runner.py --benchmarks tests/evaluation/benchmarks.jsonl --output results/test_eval.json --mock`
7. Author your report in `handoff.md` and send a message back.
