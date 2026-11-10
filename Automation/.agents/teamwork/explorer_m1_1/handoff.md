# Handoff Report: StateManager Difficulty Filtering & Test Strategy

**Milestone**: Milestone 1: Filtering & Extractor Foundation  
**Agent**: Explorer 1 (`explorer_m1_1`)  
**Target File**: `zenclass_guvi/core/state_manager.py`  
**Test Suite**: `zenclass_guvi/tests/test_m1_filtering.py`  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi`  
**Date**: 2026-11-10T22:35:00Z  

---

## 1. Observation

### 1.1 `core/state_manager.py` Schema & Task Data Structures

Direct inspection of `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/core/state_manager.py` reveals:

1. **Table Definition** (`core/state_manager.py:149-165`):
   ```sql
   CREATE TABLE IF NOT EXISTS tasks (
       task_id TEXT PRIMARY KEY,
       platform TEXT NOT NULL,
       task_category TEXT NOT NULL,
       title TEXT NOT NULL,
       url TEXT NOT NULL DEFAULT '',
       status TEXT NOT NULL,
       attempt_count INTEGER NOT NULL DEFAULT 0,
       result TEXT NOT NULL DEFAULT '',
       failure_reason TEXT,
       next_action TEXT NOT NULL DEFAULT '',
       time_spent_seconds REAL NOT NULL DEFAULT 0.0,
       metadata JSON,
       created_at TEXT NOT NULL,
       updated_at TEXT NOT NULL
   );
   ```

2. **Existing Indexes** (`core/state_manager.py:167-169`):
   ```sql
   CREATE INDEX IF NOT EXISTS idx_tasks_platform_status ON tasks(platform, status);
   CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
   CREATE INDEX IF NOT EXISTS idx_tasks_updated_at ON tasks(updated_at);
   ```

3. **`TaskRecord` Dataclass** (`core/state_manager.py:51-90`):
   Contains `metadata: Dict[str, Any] = field(default_factory=dict)` alongside property aliases `attempts` and `category`. Serialization helper `to_dict()` outputs all 9 mandatory Requirement R3 fields (`platform`, `task_id`, `category`, `status`, `attempts`, `result`, `timestamp`, `failure_reason`, `next_action`).

4. **Current `list_pending` Implementation** (`core/state_manager.py:471-493`):
   ```python
   def list_pending(
       self,
       platform: Optional[str] = None,
       limit: Optional[int] = None
   ) -> List[TaskRecord]:
       """Returns all pending/discovered/redo tasks ready for execution."""
       with self._lock:
           cursor = self.conn.cursor()
           query = "SELECT * FROM tasks WHERE LOWER(status) IN ('pending', 'discovered', 'redo', 'in_progress')"
           params: List[Any] = []

           if platform:
               query += " AND LOWER(platform) = ?"
               params.append(platform.lower())

           query += " ORDER BY created_at ASC"
           if limit is not None:
               query += " LIMIT ?"
               params.append(limit)

           cursor.execute(query, params)
           return [self._row_to_task(row) for row in cursor.fetchall()]
   ```

5. **Current `get_pending_tasks` Alias** (`core/state_manager.py:494-496`):
   ```python
   def get_pending_tasks(self, platform: Optional[str] = None) -> List[TaskRecord]:
       """Alias satisfying PROJECT.md interface contract."""
       return self.list_pending(platform=platform)
   ```

### 1.2 Metadata Column Structure in Live Codebase

Inspection across drivers and live database reveals the exact JSON layout of `metadata`:

1. **Guvi CodeKata Tasks** (`zenclass_guvi/drivers/guvi_driver.py:509-515`):
   ```python
   "metadata": {
       "slug": slug,
       "difficulty": difficulty,      # Extracted from <td class="difficulty">, e.g. "Easy", "Medium", "Hard"
       "points": points,              # Extracted from <td class="points">, e.g. "30"
       "success_rate": success_rate,  # e.g. "78%"
       "page_number": page_num,       # e.g. 1
   }
   ```
   In `guvi_driver.py:482`, difficulty is extracted via:
   `difficulty = col3.inner_text().strip() if col3 else "Easy"`

2. **Downstream Callers Relying on `list_pending`** (`zenclass_guvi/drivers/guvi_driver.py:896-907`):
   ```python
   existing_pending = (
       self.state_manager.list_pending(platform="guvi", limit=limit)
       if self.state_manager
       else []
   )
   if existing_pending:
       logger.info(f"Retrieved {len(existing_pending)} pending Guvi task(s) from SQLite StateManager.")
       for t in existing_pending:
           slug = t.metadata.get("slug") if t.metadata else None
           if not slug:
               slug = t.task_id.replace("guvi-", "").strip("/")
           pending_slugs.append(slug)
   ```
   **Critical**: Downstream expects `t.metadata.get("slug")` and `t.task_id`. Therefore, `list_pending` must continue returning `List[TaskRecord]` instances.

3. **Live Database Inspection** (`data/automation_state.db`):
   - Total rows in `tasks`: 38
   - Guvi CodeKata: 15 tasks (`status='COMPLETED'`, `difficulty='Easy'`)
   - ZenClass Tasks & Projects: 23 tasks (`status='COMPLETED'` or `'BLOCKED'`, `difficulty=None`)
   - Confirming that ZenClass tasks do not store a `difficulty` field.

### 1.3 SQLite Engine Capabilities & Edge Case Verification

Direct execution on the host macOS machine:
- Host Python: `/usr/bin/python3` (Python 3.9.6)
- Host Pytest: `/Users/devesh/Library/Python/3.9/bin/pytest` (pytest 8.4.2)
- SQLite Engine: version 3.51.0 with native JSON support enabled (`json_extract` and `json_valid`).
- **Empirical Edge Case**: If `metadata` contains an empty string `""` or invalid JSON, calling `json_extract(metadata, '$.difficulty')` raises `sqlite3.OperationalError: malformed JSON`.
- **Empirical Safe Construct**:
  ```sql
  CASE 
      WHEN metadata IS NOT NULL AND json_valid(metadata) = 1 
      THEN LOWER(json_extract(metadata, '$.difficulty')) 
      ELSE NULL 
  END IN (?, ...)
  ```
  Testing this against rows with `""`, `NULL`, `"{invalid}"`, and `{"difficulty": "Medium"}` returns matching rows cleanly without raising any exceptions.

### 1.4 Test Baseline

Executing the full existing test suite:
- Command: `/Users/devesh/Library/Python/3.9/bin/pytest tests/`
- Result: `268 passed in 69.39s` (0 failures, 0 regressions).
- Findings on existing test coverage:
  - `tests/test_m1_core.py` (22 tests): Verifies StateManager WAL mode, 9 fields, update status, batch insert, summary stats, atomic JSON export, thread safety. None of these tests exercise `list_pending` or difficulty filtering.
  - `tests/e2e/tier1_features/test_f02_state_manager.py` (4 tests): Tests `get_pending_tasks("zenclass")` filtering out completed tasks, but does not test `difficulties`.
  - `tests/test_m1_filtering.py`: Does not currently exist.

---

## 2. Logic Chain

1. **Problem Requirement**:
   The system must solve Medium and Hard difficulty practice questions on Guvi CodeKata without processing Easy or completed items, filtering at the database query level.

2. **Persistence Schema**:
   `StateManager` persists task records in SQLite `tasks` table with a `metadata JSON` column. For Guvi CodeKata tasks, `metadata` stores `{"difficulty": "Easy"|"Medium"|"Hard", ...}`.

3. **Query Optimization**:
   Filtering tasks via SQL `json_extract` rather than in Python memory avoids fetching thousands of catalog tasks into memory during large-scale runs (e.g. 2,145 CodeKata tasks across 143 pages).

4. **Case-Insensitive Normalization**:
   The user or CLI may supply difficulties with mixed casing (e.g. `["Medium", "Hard"]`, `["medium", "hard"]`, or CLI `--difficulty Medium,Hard`). Normalizing the database field with `LOWER(...)` and normalizing input parameters with `.strip().lower()` ensures exact case-insensitive matching regardless of capitalization.

5. **Crash-Proof JSON Handling**:
   Because SQLite's `json_extract` raises an `OperationalError` on malformed JSON or empty string values, wrapping the extraction in a conditional `CASE WHEN metadata IS NOT NULL AND json_valid(metadata) = 1 THEN ... ELSE NULL END` guarantees zero query failures even if malformed or non-JSON records exist in the table.

6. **Preserving Backward Compatibility**:
   When `difficulties` is `None` or an empty list `[]` (or contains only empty strings), the query must omit the difficulty filter entirely, ensuring that:
   - Existing ZenClass tasks (which have no `difficulty` key) are still returned by `list_pending("zenclass")`.
   - Existing tests and caller functions without `difficulties` continue to pass without behavioral regression.

7. **Contract & Interface Alignment**:
   `get_pending_tasks` is an alias for `list_pending` across tests and contract harnesses. Adding `difficulties: Optional[List[str]] = None` to `get_pending_tasks` maintains complete API parity.

---

## 3. Caveats

1. **Tasks with Missing or Non-string Difficulty**:
   If a task's `metadata` lacks a `difficulty` key (or `metadata` is `None`), `json_extract(metadata, '$.difficulty')` returns `NULL`. SQL `NULL IN (...)` evaluates to UNKNOWN (filtered out by `WHERE`). This is correct: when filtering by `["Medium", "Hard"]`, tasks without an explicit matching difficulty must not be selected.
2. **Whitespace and Empty Strings**:
   If a caller passes `difficulties=["   ", ""]`, this should be sanitized to an empty list and treated as no filter (preserving backward compatibility).
3. **Read-Only Explorer Discipline**:
   In strict compliance with the Explorer role, no production files were modified. All proposals below are concrete code designs for the Implementer.

---

## 4. Conclusion & Concrete Recommendations

### 4.1 Proposed Implementation for `zenclass_guvi/core/state_manager.py`

#### Updated Method Signatures & Implementation

In `zenclass_guvi/core/state_manager.py`:

```python
    def list_pending(
        self,
        platform: Optional[str] = None,
        limit: Optional[int] = None,
        difficulties: Optional[List[str]] = None
    ) -> List[TaskRecord]:
        """
        Returns all pending/discovered/redo/in_progress tasks ready for execution.
        
        Args:
            platform: Optional platform filter (e.g. 'guvi', 'zenclass').
            limit: Optional maximum number of tasks to return.
            difficulties: Optional list of difficulty strings (e.g. ['Medium', 'Hard']).
                          Case-insensitive. When None or empty, no difficulty filter is applied.
        """
        with self._lock:
            cursor = self.conn.cursor()
            query = "SELECT * FROM tasks WHERE LOWER(status) IN ('pending', 'discovered', 'redo', 'in_progress')"
            params: List[Any] = []

            if platform:
                query += " AND LOWER(platform) = ?"
                params.append(platform.lower())

            if difficulties:
                cleaned_diffs = [
                    d.strip().lower()
                    for d in difficulties
                    if isinstance(d, str) and d.strip()
                ]
                if cleaned_diffs:
                    placeholders = ", ".join(["?"] * len(cleaned_diffs))
                    query += f""" AND CASE 
                        WHEN metadata IS NOT NULL AND json_valid(metadata) = 1 
                        THEN LOWER(json_extract(metadata, '$.difficulty')) 
                        ELSE NULL 
                    END IN ({placeholders})"""
                    params.extend(cleaned_diffs)

            query += " ORDER BY created_at ASC"
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)

            cursor.execute(query, params)
            return [self._row_to_task(row) for row in cursor.fetchall()]

    def get_pending_tasks(
        self,
        platform: Optional[str] = None,
        difficulties: Optional[List[str]] = None
    ) -> List[TaskRecord]:
        """Alias satisfying PROJECT.md interface contract with optional difficulty filtering."""
        return self.list_pending(platform=platform, difficulties=difficulties)
```

#### Optional Query Optimization Index (for `_init_db`)
In `StateManager._init_db()` (`core/state_manager.py:167-170`), the implementer can optionally add an expression index:
```sql
cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_difficulty ON tasks(LOWER(json_extract(metadata, '$.difficulty')));")
```

---

### 4.2 Comprehensive Test Specification for `tests/test_m1_filtering.py`

Create a dedicated test file `zenclass_guvi/tests/test_m1_filtering.py` with 12 distinct unit test cases covering all requirements and boundaries:

```python
"""
tests/test_m1_filtering.py - Unit and Integration Tests for Milestone 1 Filtering
Verifies StateManager.list_pending difficulty filtering, case insensitivity,
backward compatibility, and edge cases.
"""

import os
import json
import shutil
import tempfile
import unittest
from core.state_manager import StateManager, TaskStatus, TaskResult


class TestStateManagerDifficultyFiltering(unittest.TestCase):
    """Verifies difficulty filtering in StateManager.list_pending() and get_pending_tasks()."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_m1_filter_")
        self.db_path = os.path.join(self.temp_dir, "test_state.db")
        self.sm = StateManager(db_path=self.db_path)

        # Seed test tasks
        # 1. Easy Guvi task (pending)
        self.sm.record_task(
            task_id="guvi-easy-1",
            platform="guvi",
            title="Problem Easy 1",
            category="CodeKata",
            status="pending",
            metadata={"difficulty": "Easy", "slug": "easy-1"}
        )
        # 2. Medium Guvi task (discovered)
        self.sm.record_task(
            task_id="guvi-med-1",
            platform="guvi",
            title="Problem Medium 1",
            category="CodeKata",
            status="discovered",
            metadata={"difficulty": "Medium", "slug": "med-1"}
        )
        # 3. Hard Guvi task (redo, uppercase difficulty)
        self.sm.record_task(
            task_id="guvi-hard-1",
            platform="guvi",
            title="Problem Hard 1",
            category="CodeKata",
            status="redo",
            metadata={"difficulty": "HARD", "slug": "hard-1"}
        )
        # 4. Completed Medium Guvi task (must be filtered out by status)
        self.sm.record_task(
            task_id="guvi-med-completed",
            platform="guvi",
            title="Problem Medium Completed",
            category="CodeKata",
            status="completed",
            metadata={"difficulty": "Medium", "slug": "med-comp"}
        )
        # 5. ZenClass task with no difficulty (pending)
        self.sm.record_task(
            task_id="zen-task-1",
            platform="zenclass",
            title="ZenClass Task 1",
            category="Tasks",
            status="pending",
            metadata={"tags": ["javascript"]}
        )
        # 6. Task with empty metadata dict (pending)
        self.sm.record_task(
            task_id="empty-meta-1",
            platform="guvi",
            title="Empty Meta Task",
            category="CodeKata",
            status="pending",
            metadata={}
        )

    def tearDown(self):
        self.sm.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_backward_compatibility_none_difficulties(self):
        """When difficulties is None, all pending tasks across all difficulties and platforms are returned."""
        tasks = self.sm.list_pending()
        task_ids = [t.task_id for t in tasks]
        self.assertEqual(len(tasks), 5)  # guvi-easy-1, guvi-med-1, guvi-hard-1, zen-task-1, empty-meta-1
        self.assertNotIn("guvi-med-completed", task_ids)

    def test_02_backward_compatibility_empty_list_difficulties(self):
        """When difficulties is [], no difficulty filtering is applied (preserves backward compatibility)."""
        tasks = self.sm.list_pending(difficulties=[])
        self.assertEqual(len(tasks), 5)

    def test_03_single_difficulty_filtering(self):
        """Filter by ['Medium'] returns only the pending Medium task."""
        tasks = self.sm.list_pending(difficulties=["Medium"])
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_id, "guvi-med-1")
        self.assertEqual(tasks[0].metadata.get("difficulty"), "Medium")

    def test_04_multiple_difficulties_filtering(self):
        """Filter by ['Medium', 'Hard'] returns both Medium and Hard pending tasks."""
        tasks = self.sm.list_pending(difficulties=["Medium", "Hard"])
        task_ids = [t.task_id for t in tasks]
        self.assertEqual(len(tasks), 2)
        self.assertIn("guvi-med-1", task_ids)
        self.assertIn("guvi-hard-1", task_ids)
        self.assertNotIn("guvi-easy-1", task_ids)
        self.assertNotIn("zen-task-1", task_ids)

    def test_05_case_insensitivity_filtering(self):
        """Parameters ['medium', 'hard'] match 'Medium' and 'HARD' in database."""
        tasks = self.sm.list_pending(difficulties=["medium", "hard"])
        task_ids = [t.task_id for t in tasks]
        self.assertEqual(len(tasks), 2)
        self.assertIn("guvi-med-1", task_ids)
        self.assertIn("guvi-hard-1", task_ids)

    def test_06_whitespace_handling_in_difficulties(self):
        """Surrounding whitespace in difficulties strings is stripped cleanly."""
        tasks = self.sm.list_pending(difficulties=["  Medium  ", "Hard\n"])
        task_ids = [t.task_id for t in tasks]
        self.assertEqual(len(tasks), 2)
        self.assertIn("guvi-med-1", task_ids)
        self.assertIn("guvi-hard-1", task_ids)

    def test_07_whitespace_only_difficulties_treated_as_empty(self):
        """A list containing only whitespace/empty strings falls back to returning all pending tasks."""
        tasks = self.sm.list_pending(difficulties=["", "   "])
        self.assertEqual(len(tasks), 5)

    def test_08_unknown_difficulty_returns_empty_list(self):
        """Querying an unknown difficulty (e.g. ['Expert']) returns an empty list without error."""
        tasks = self.sm.list_pending(difficulties=["Expert"])
        self.assertEqual(tasks, [])

    def test_09_tasks_without_difficulty_excluded_when_difficulties_specified(self):
        """Tasks lacking 'difficulty' key in metadata (e.g. ZenClass tasks) are excluded."""
        tasks = self.sm.list_pending(difficulties=["Easy"])
        task_ids = [t.task_id for t in tasks]
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_id, "guvi-easy-1")
        self.assertNotIn("zen-task-1", task_ids)
        self.assertNotIn("empty-meta-1", task_ids)

    def test_10_combined_platform_limit_and_difficulties(self):
        """Combined filtering with platform='guvi', difficulties=['Medium', 'Hard'], limit=1."""
        tasks = self.sm.list_pending(platform="guvi", difficulties=["Medium", "Hard"], limit=1)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_id, "guvi-med-1")

    def test_11_get_pending_tasks_alias_parity(self):
        """get_pending_tasks alias supports difficulties argument identically."""
        tasks = self.sm.get_pending_tasks(platform="guvi", difficulties=["Medium"])
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_id, "guvi-med-1")

    def test_12_malformed_metadata_resilience(self):
        """Malformed or non-JSON metadata strings do not crash SQLite query."""
        cursor = self.sm.conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (task_id, platform, task_category, title, status, metadata, created_at, updated_at) "
            "VALUES ('bad-json-task', 'guvi', 'CodeKata', 'Bad Task', 'pending', '{corrupt json', '2026-01-01', '2026-01-01');"
        )
        # Should not raise sqlite3.OperationalError: malformed JSON
        tasks = self.sm.list_pending(difficulties=["Medium"])
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_id, "guvi-med-1")
```

---

## 5. Verification Method

### 5.1 Test Execution Commands
The implementer and test runner can verify the implementation and ensure 0 regressions using:

1. **Verify M1 Filtering Test Suite**:
   ```sh
   cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
   /Users/devesh/Library/Python/3.9/bin/pytest tests/test_m1_filtering.py -v
   ```
   **Expected**: 12/12 passing tests.

2. **Verify Full Baseline Regression Suite**:
   ```sh
   cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
   /Users/devesh/Library/Python/3.9/bin/pytest tests/
   ```
   **Expected**: 280/280 passing tests (268 baseline + 12 new M1 tests).

### 5.2 Files to Inspect
- `zenclass_guvi/core/state_manager.py` (lines 471-496)
- `zenclass_guvi/tests/test_m1_filtering.py`

### 5.3 Invalidation Conditions
- Any change to `list_pending` that returns raw dictionaries instead of `TaskRecord` instances will break `drivers/guvi_driver.py:904` (`t.metadata.get("slug")`).
- Directly querying `json_extract(metadata, '$.difficulty')` without `json_valid(metadata)` check will fail if any row contains un-serialized strings or empty string metadata.
- Omitting `cleaned_diffs` fallback when `difficulties` is `[]` or `[""]` will break backward compatibility for callers expecting all pending tasks.
