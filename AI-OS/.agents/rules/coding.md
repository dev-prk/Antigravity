# Coding Standards & Runtime Constraints

## 1. Runtime Environment
1. **Python 3.9 Standard Library Mandate**:
   - All runtime code in `aios/` must run cleanly on Python 3.9.6 using exclusively the Python standard library.
   - Zero external third-party pip dependencies in runtime packages (no `pydantic`, `docker`, `psycopg2`, `langgraph`, `openai`, `requests`).
   - Pytest is used strictly as the external test runner in `tests/`.

2. **Syntax Compatibility**:
   - Do NOT use Python 3.10+ syntax features:
     - No structural pattern matching (`match` / `case` statements).
     - No bare union type syntax (e.g. `int | str`) unless guarded with `from __future__ import annotations`. Use `typing.Union`, `typing.Optional`, `typing.List`, `typing.Dict`.
     - No Python 3.10 dataclass arguments (e.g. `slots=True`, `kw_only=True`).

3. **Data Modeling & Serialization**:
   - Define data models using standard library `@dataclass(frozen=True)` or `@dataclass`.
   - Provide standard `.to_dict()` and `.from_dict()` serialization methods for JSON compatibility.

4. **Database Operations**:
   - Use Python's built-in `sqlite3` module.
   - Enable WAL mode (`PRAGMA journal_mode=WAL;`) and foreign keys (`PRAGMA foreign_keys=ON;`).
   - Wrap mutating database interactions in atomic transactions (`with conn:`).
