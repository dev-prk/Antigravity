# Scope: Milestone 1: Filtering & Extractor Foundation

## Architecture
- `core/state_manager.py`: SQLite persistence (`tasks`, `task_attempts`, `execution_runs`), difficulty filtering in `list_pending(platform=..., limit=..., difficulties=...)`.
- `solver/extractor.py`: DOM and regex extraction of problem spec, CSS style sanitization (`{display:inline-flex...}`).
- `config.py`: Headless browser config constants and defaults.
- `main.py`: CLI `--difficulty` and `--headless` argument parsing and propagation.
- `tests/test_m1_filtering.py`: Unit and integration test suite verifying M1 features.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Headless Background Execution | Default/configurable headless mode | M1 | Survey Explorer 1, 3 |
| 2 | Difficulty Filtering in StateManager | Support `difficulties` parameter in `StateManager.list_pending()` | M1 | Survey Explorer 1, 2 |
| 3 | Extractor CSS Sanitization | Sanitize inline style noise from sample input/output | M1 | Survey Explorer 3 |
| 4 | CLI Difficulty & Headless Options | Expose `--difficulty` and `--headless` flags in `run-codekata` | M1 | Survey Explorer 1, 2 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Filtering & Extractor Foundation | `core/state_manager.py`, `solver/extractor.py`, `main.py`, `config.py`, `tests/test_m1_filtering.py` | none | IN_PROGRESS |

## Interface Contracts
### `core/state_manager.py` ↔ `drivers/guvi_driver.py`
- `list_pending(platform: Optional[str] = None, limit: Optional[int] = None, difficulties: Optional[List[str]] = None) -> List[Dict[str, Any]]`:
  When `difficulties` is provided, filters tasks where `json_extract(metadata, '$.difficulty') IN (...)` (case-insensitive).

### `solver/extractor.py` ↔ `solver/code_generator.py`
- `ProblemSpecification`:
  `sample_cases` must contain sanitized inputs and outputs, free of CSS style leaks (`{display:inline-flex...}`).

### `config.py` & `main.py`
- CLI flag `--difficulty` supports multiple difficulties or comma-separated strings (e.g. `Medium,Hard`), passed down to runner.
- `--headless` default or boolean flag for background headless execution.
