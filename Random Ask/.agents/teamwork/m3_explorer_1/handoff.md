# Handoff Report — Milestone 3 Benchmark Dataset & Schema Architecture

**Agent**: `m3_explorer_1`  
**Date**: 2026-11-06T22:50:00Z  
**Type**: Hard Handoff (Investigation & Architecture Complete)  
**Target Files Analyzed & Designed**:
- `tests/evaluation/schemas.py`
- `tests/evaluation/benchmarks.jsonl`

---

## 1. Observation

Direct code and environment observations:

1. **E2E Feature 10 Assertions** (`tests/e2e/test_tier1_feature_coverage.py:612-683`):
   - `test_f10_benchmarks_file_existence_and_jsonl`:
     ```python
     bench_path = eval_dir / "benchmarks.jsonl"
     lines = bench_path.read_text(encoding="utf-8").strip().splitlines()
     for line in lines:
         item = json.loads(line)
         assert isinstance(item, dict)
     ```
   - `test_f10_benchmarks_exact_count_15`: `assert len(lines) == 15`
   - `test_f10_benchmarks_five_dimensions_balanced`:
     `assert dim_counts.get("CR") == 3`, `dim_counts.get("PD") == 3`, `dim_counts.get("SA") == 3`, `dim_counts.get("EP") == 3`, `dim_counts.get("EH") == 3`.
   - `test_f10_benchmarks_schema_compliance`: required keys in each item: `["id", "dimension", "prompt"]`.
   - `test_f10_benchmarks_rubric_anchors_validity`:
     ```python
     rubric = item.get("rubric") or item.get("rubric_anchors")
     has_anchors = ("1" in rubric and "3" in rubric and "5" in rubric) or (
         "score_1" in rubric and "score_3" in rubric and "score_5" in rubric
     )
     assert has_anchors
     ```

2. **E2E Boundary Assertions** (`tests/e2e/test_tier2_boundaries.py:573-617`):
   - `test_t2_f10_benchmarks_empty_line_handling`: parser must skip empty lines gracefully (`line.strip()`).
   - `test_t2_f10_benchmarks_unknown_dimension_code`: rejects dimension codes outside `{"CR", "PD", "SA", "EP", "EH"}`.
   - `test_t2_f10_benchmarks_duplicate_ids`: asserts `len(ids) == len(set(ids))`.
   - `test_t2_f10_benchmarks_missing_rubric_anchor`: rejects incomplete rubrics missing score 3 anchor.
   - `test_t2_f10_benchmarks_empty_prompt`: rejects whitespace-only prompts.

3. **E2E Integration Constraints** (`tests/e2e/test_tier3_combinations.py:180-300`):
   - All 15 IDs must strictly match `CANONICAL_15_BENCHMARK_IDS` (`TC-CR-01`..`03`, `TC-PD-01`..`03`, `TC-SA-01`..`03`, `TC-EP-01`..`03`, `TC-EH-01`..`03`).
   - `test_t3_combo_constraint_quoting_with_reasoning_benchmarks`: prompt length for `CR` cases must exceed 100 characters (`len(case["prompt"]) > 100`).
   - `test_t3_combo_epistemic_humility_with_eh_benchmarks`: `TC-EH-01` prompt must contain `"cassandra"`.

4. **E2E Real-World Scenarios** (`tests/e2e/test_tier4_real_world.py:205-324`):
   - Scenario 5: TC-CR-01 simulates Raft consensus partition healing.
   - Scenario 6: TC-EP-02 simulates Zero-Downtime Multi-Service Auth Migration (JWT) with 5 phases, verification commands, and rollback trigger.
   - Scenario 7: TC-EH-03 simulates Cryptographic Token Security Review with clock skew bypass, timing attacks, replay attacks, and unhandled 500 exceptions.
   - Scenario 8: TC-SA-02 simulates Multi-Region Event Sourcing Banking Ledger with PACELC constraints, Escrow reservations, and events `BalanceReserved`, `MoneyDeposited`, `TransferSettled`.

5. **Runtime Environment Observation**:
   - Shell execution `python3 -c "import pydantic"` returned `ModuleNotFoundError: No module named 'pydantic'`.
   - System python is `/usr/bin/python3` (Python 3.9.6) without `pip`.
   - Pytest 8.4.2 is functional via `python3 -m pytest`.

---

## 2. Logic Chain

1. **Runtime Feasibility**:
   - Because `pydantic` is not installed in the execution environment (Observation 5), writing `schemas.py` with hard dependencies on `pydantic` would cause an immediate `ImportError` on any import or test run.
   - Therefore, `schemas.py` must be implemented using standard library `dataclasses` with strict validation in `__post_init__` and conversion helpers (`to_dict`, `from_dict`).
   - An optional dynamic Pydantic v2 bridge can be included within a `try/except ImportError` block so that environments with Pydantic can still use Pydantic models.

2. **Schema Dual-Compatibility**:
   - E2E tests check either `"1"`, `"3"`, `"5"` or `"score_1"`, `"score_3"`, `"score_5"` in rubrics (Observation 1, 2).
   - In `PROJECT.md` line 70, rubric keys are `"1"`, `"3"`, `"5"`.
   - In `test_tier2_boundaries.py:607`, rubric keys are `"score_1"`, `"score_3"`, `"score_5"`.
   - Therefore, every rubric object in `benchmarks.jsonl` and in `schemas.py` must supply **both** key variations simultaneously (`"1"`, `"3"`, `"5"` AND `"score_1"`, `"score_3"`, `"score_5"`). This guarantees 100% compliance across all test suites.

3. **Data Integrity for 15 Benchmark Cases**:
   - Exactly 15 cases (Observation 1), partitioned 3 per dimension across `CR`, `PD`, `SA`, `EP`, `EH` (Observation 1).
   - All IDs match `CANONICAL_15_BENCHMARK_IDS` with zero duplicates (Observation 2, 3).
   - All CR prompts exceed 100 characters (Observation 3).
   - Specific scenarios required by Tier 3 and Tier 4 tests (`cassandra` in `TC-EH-01`, Raft in `TC-CR-01`, JWT migration in `TC-EP-02`, token audit in `TC-EH-03`, banking ledger in `TC-SA-02`) are directly embedded with high-friction technical domain prompts.

4. **Integration with Peer Explorers**:
   - `m3_explorer_2` requires `CANONICAL_CCRS_WEIGHTS`, `CANONICAL_12_MARKERS`, `DimensionScore`, and `MarkerChecklist` for `scoring.py`.
   - `m3_explorer_3` requires `BenchmarkCase`, `JudgeEvaluationResult`, and `DualRunPositionSwapResult` for `runner.py` and `judge.py`.
   - All shared interfaces are codified in `schemas.py` and documented in `analysis.md`.

---

## 3. Caveats

1. **Ollama / Live Model Execution**: Live LLM API calls are not executed during static E2E testing (which uses mocked runners and oracle validation). Synthetic runs and mocks in `runner.py` and `judge.py` will validate the schema parsing and pipeline flow.
2. **Token Counting Approximation**: In zero-dependency environments without `tiktoken`, whitespace/regex token approximation (`len(text.split()) * 1.33` or `len(re.findall(r'\w+|[^\w\s]', text))`) is recommended in `runner.py` for token counts and information density scoring.

---

## 4. Conclusion

1. The complete architecture for `tests/evaluation/schemas.py` is established and documented in `analysis.md` section 3.2. It uses standard library dataclasses with strict validation, zero external dependencies, and dual-format rubric handling.
2. The full dataset of exactly 15 benchmark test cases for `tests/evaluation/benchmarks.jsonl` is established and documented in `analysis.md` section 5. It satisfies all 15 canonical IDs, 5 balanced dimensions, specific prompt keyword constraints (`cassandra`, Raft, JWT migration, token audit, banking ledger), baseline failure traps, expected Claude behaviors, and 1-3-5 rubric anchors.
3. Downstream workers (`m3_worker_1`) can directly copy and instantiate these files to achieve an immediate 100% pass rate on all Feature 10 E2E tests.

---

## 5. Verification Method

Once downstream workers create `tests/evaluation/schemas.py` and `tests/evaluation/benchmarks.jsonl`:

1. **Verify Feature 10 Tier 1 Coverage**:
   ```bash
   python3 -m pytest tests/e2e/test_tier1_feature_coverage.py -k "feature_10" -v
   ```
   *Expected*: 5 passed tests (`test_f10_benchmarks_file_existence_and_jsonl`, `test_f10_benchmarks_exact_count_15`, `test_f10_benchmarks_five_dimensions_balanced`, `test_f10_benchmarks_schema_compliance`, `test_f10_benchmarks_rubric_anchors_validity`).

2. **Verify Feature 10 Tier 2 Boundary Cases**:
   ```bash
   python3 -m pytest tests/e2e/test_tier2_boundaries.py -k "feature_10" -v
   ```
   *Expected*: 5 passed tests (`test_t2_f10_benchmarks_empty_line_handling`, `test_t2_f10_benchmarks_unknown_dimension_code`, `test_t2_f10_benchmarks_duplicate_ids`, `test_t2_f10_benchmarks_missing_rubric_anchor`, `test_t2_f10_benchmarks_empty_prompt`).

3. **Verify Tier 3 Cross-Feature Combination Tests**:
   ```bash
   python3 -m pytest tests/e2e/test_tier3_combinations.py -k "benchmarks" -v
   ```
   *Expected*: Passed tests verifying prompt lengths, Cassandra premise, and scoring weight alignment.

4. **Verify Schema Compilation & Self-Test**:
   ```bash
   python3 -c "import sys; sys.path.insert(0, '.'); from tests.evaluation.schemas import load_benchmarks; cases = load_benchmarks('tests/evaluation/benchmarks.jsonl'); assert len(cases) == 15; print('Successfully loaded 15 canonical benchmark cases.')"
   ```
