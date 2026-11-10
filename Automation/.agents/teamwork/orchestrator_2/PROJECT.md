# Project: Guvi CodeKata Medium & Hard Headless Automation

## Architecture
- `core/browser.py`: Playwright headless browser manager, stealth flags, cookie session restoration.
- `core/state_manager.py`: SQLite persistence (`tasks`, `task_attempts`, `execution_runs`), difficulty filtering in `list_pending()`.
- `solver/extractor.py`: DOM and regex extraction of problem spec, CSS sanitization.
- `solver/code_generator.py`: Python 3 solution generation for Medium and Hard questions, error feedback refinement.
- `drivers/guvi_driver.py`: CodeKata catalog discovery (Medium/Hard filtering), 3-attempt retry loop in `solve_problem()`, Ace Editor injection, Run Code and Submit verification, state recording.
- `main.py` & `config.py`: CLI arguments (`--difficulty`, `--headless`), headless execution defaults for CodeKata.

## Code Layout
- `zenclass_guvi/config.py`: Configuration constants. Owned by M1.
- `zenclass_guvi/core/state_manager.py`: SQLite persistence and query interface. Owned by M1.
- `zenclass_guvi/solver/extractor.py`: Problem extraction and input sanitization. Owned by M1.
- `zenclass_guvi/main.py`: Command line interface. Owned by M1.
- `zenclass_guvi/solver/code_generator.py`: Solution synthesis for Python 3. Owned by M2.
- `zenclass_guvi/drivers/guvi_driver.py`: Platform driver, catalog discovery, 3-attempt retry loop. Owned by M3.
- `zenclass_guvi/tests/`: Pytest suites and E2E verification. Owned by M4.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Headless Background Execution | Run browser automation entirely headlessly (`headless=True`) without visible UI windows or desktop interference | M1, M3 | Survey Explorer 1, 3 |
| 2 | Difficulty Filtering in StateManager | Support `difficulties` parameter in `StateManager.list_pending(platform="guvi", difficulties=["Medium", "Hard"])` | M1 | Survey Explorer 1, 2 |
| 3 | Extractor CSS Sanitization | Prevent inline stylesheet strings from polluting `sample_input` / `sample_output` in `solver/extractor.py` | M1 | Survey Explorer 3 |
| 4 | CLI Difficulty & Headless Options | Expose `--difficulty` in `main.py run-codekata` and ensure `--headless` defaults properly | M1 | Survey Explorer 1, 2 |
| 5 | Medium & Hard Code Generation | Implement Python 3 code generation for algorithmic Medium and Hard CodeKata problems in `solver/code_generator.py` | M2 | Survey Explorer 1, 2, 3 |
| 6 | Solver Retry Feedback Refinement | Accept previous error output in `generate_solution(spec, previous_error=...)` to refine candidate code | M2 | Survey Explorer 2, 3 |
| 7 | Difficulty Filtering in Discovery & Pipeline | Support `difficulties` parameter in `GuviDriver.discover_catalog()` and `GuviDriver.run_pipeline()` | M3 | Survey Explorer 2 |
| 8 | 3-Attempt Retry Loop | In `GuviDriver.solve_problem()`, retry generating and submitting up to 3 times per problem before recording final failure | M3 | Survey Explorer 1, 3 |
| 9 | Granular State & Test Output Persistence | Save each attempt's test outputs, duration, status, and code snapshots into `data/automation_state.db` | M3 | Survey Explorer 3 |
| 10 | Regression & E2E Verification | Ensure 100% passing across existing 268 tests and verify new Medium/Hard headless functionality | M4 | Survey Explorer 1, 2, 3 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Filtering & Extractor Foundation | `core/state_manager.py`, `solver/extractor.py`, `main.py`, `config.py` | none | PLANNED |
| M2 | Intelligent Solver & Error Adaptation | `solver/code_generator.py` | none | PLANNED |
| M3 | Headless Driver 3-Attempt Pipeline | `drivers/guvi_driver.py` | M1, M2 | PLANNED |
| M4 | Final E2E Verification & Hardening | Full test suite verification, headless validation | M3 | PLANNED |

## Interface Contracts
### `core/state_manager.py` ↔ `drivers/guvi_driver.py`
- `list_pending(platform: Optional[str] = None, limit: Optional[int] = None, difficulties: Optional[List[str]] = None) -> List[Dict[str, Any]]`:
  When `difficulties` is provided, filters tasks where `json_extract(metadata, '$.difficulty') IN (...)` (case-insensitive).
- `record_task_attempt(...)`:
  Persists attempt number, timestamp, status, result, failure reason, code snapshot, and `details` JSON containing per-test-case validation results.

### `solver/extractor.py` ↔ `solver/code_generator.py`
- `ProblemSpecification`:
  `sample_cases` must contain sanitized inputs and outputs, free of CSS style leaks (`{display:inline-flex...}`).

### `solver/code_generator.py` ↔ `drivers/guvi_driver.py`
- `generate_solution(spec: ProblemSpecification, previous_error: Optional[str] = None, attempt: int = 1) -> GeneratedSolution`:
  Returns `GeneratedSolution(code=..., confidence=..., strategy=..., language="PYTHON 3")`.
  Capable of generating Python 3 solutions for Medium and Hard problems and adjusting code based on `previous_error`.

### `drivers/guvi_driver.py` ↔ `main.py`
- `GuviDriver.run_pipeline(limit=..., category=..., task_id=..., max_pages=..., difficulties=["Medium", "Hard"])`:
  Runs discovery and problem solving filtered by `difficulties`.
