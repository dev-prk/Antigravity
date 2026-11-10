# Scope: Milestone 2 — Intelligent Solver & Error Adaptation

## Architecture
- Module: `solver/code_generator.py`
- Test: `tests/test_m2_code_generator.py`
- Purpose: Algorithmic Python 3 solution generation for Medium and Hard Guvi CodeKata problems, plus dynamic refinement based on previous execution/test error feedback.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 5 | Medium & Hard Code Generation | Implement Python 3 code generation for algorithmic Medium and Hard CodeKata problems in `solver/code_generator.py` | M2 | Survey Explorer 1, 2, 3 |
| 6 | Solver Retry Feedback Refinement | Accept previous error output in `generate_solution(spec, previous_error=..., attempt=...)` to refine candidate code | M2 | Survey Explorer 2, 3 |

## Interface Contracts
### `solver/extractor.py` ↔ `solver/code_generator.py`
- `ProblemSpecification`:
  Attributes: `title`, `description`, `input_format`, `output_format`, `constraints`, `sample_cases`, `tags`, etc.
  `sample_cases` contains sanitized inputs and expected outputs.

### `solver/code_generator.py` ↔ `drivers/guvi_driver.py`
- `generate_solution(spec: ProblemSpecification, previous_error: Optional[str] = None, attempt: int = 1) -> GeneratedSolution`:
  Returns `GeneratedSolution(code: str, confidence: float, strategy: str, language: str = "PYTHON 3")`.
  Capable of generating robust Python 3 solutions for Medium and Hard problems and adjusting code based on `previous_error` across attempts.

## Code Layout & Ownership
- Exclusive Write Ownership for M2:
  - `solver/code_generator.py`
  - `tests/test_m2_code_generator.py`
- Read-only references:
  - `solver/extractor.py`
  - `drivers/guvi_driver.py`
  - `tests/`
