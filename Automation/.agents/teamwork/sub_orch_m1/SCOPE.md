# Scope: Milestone 1 - Filtering & Extractor Foundation

## Architecture
- `core/state_manager.py`: SQLite query interface with difficulty filtering on metadata JSON.
- `solver/extractor.py`: DOM and regex parser for CodeKata problem statements with CSS style sanitization.
- `main.py` & `config.py`: CLI parser with `--difficulty` support and background headless defaults.

## Feature Inventory
| # | Feature | Description | Status |
|---|---------|-------------|--------|
| 1 | Headless Execution Config | Support headless background mode seamlessly | PLANNED |
| 2 | StateManager Difficulty Filter | `list_pending(platform='guvi', difficulties=['Medium', 'Hard'])` | PLANNED |
| 3 | Extractor CSS Sanitization | Strip `{display:inline-flex...}` from sample inputs/outputs | PLANNED |
| 4 | CLI Difficulty Option | Add `--difficulty` to `run-codekata` | PLANNED |

## Interface Contracts
- `StateManager.list_pending(platform=..., limit=..., difficulties=...)` -> `List[Dict[str, Any]]`
- `ProblemExtractor.extract(...)` -> `ProblemSpecification` with clean `sample_cases`
