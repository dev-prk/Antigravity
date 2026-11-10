# Explorer 1 Technical Investigation Report: Milestone 1 Iteration 2 Defects

- **Agent**: Explorer 1 (`explorer_m1_r2_1`)
- **Roles**: investigator, analyst
- **Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi`
- **State Folder**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m1_r2_1`
- **Handoff Type**: Hard
- **Date**: 2026-11-10T23:10:00Z
- **Assigned Scope**:
  1. `core/state_manager.py:440` in `_row_to_task` (corrupt/scalar metadata handling)
  2. `main.py:488` in `AutomationRunner.execute` (`inspect.signature` for `driver.run_pipeline`)

---

## 1. Observation

### 1.1 Defect 1: StateManager `_row_to_task` Crash on Corrupt & Scalar Metadata

**File**: `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/core/state_manager.py`  
**Line**: 440  
**Current Implementation**:
```python
    def _row_to_task(self, row: sqlite3.Row) -> TaskRecord:
        meta = json.loads(row["metadata"] or "{}") if "metadata" in row.keys() else {}
        return TaskRecord(
            task_id=row["task_id"],
            ...
            metadata=meta,
            ...
        )
```

**Verbatim Reproduction Command**:
```sh
PYTHONPATH=zenclass_guvi python3 -c "
import sqlite3, tempfile
from pathlib import Path
from core.state_manager import StateManager

with tempfile.TemporaryDirectory() as tmp:
    db = Path(tmp) / 'corrupt.db'
    sm = StateManager(db_path=str(db))
    conn = sqlite3.connect(str(db))
    conn.execute(\"\"\"
        INSERT INTO tasks (task_id, platform, task_category, title, status, metadata, created_at, updated_at)
        VALUES ('corrupt-1', 'guvi', 'Basics', 'Test', 'pending', '{corrupt json', '2026-01-01', '2026-01-01')
    \"\"\")
    conn.commit()
    conn.close()
    tasks = sm.list_pending(difficulties=None)
"
```

**Verbatim Crash Output**:
```
Traceback (most recent call last):
  File "<string>", line 16, in <module>
  File "/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/core/state_manager.py", line 508, in list_pending
    return [self._row_to_task(row) for row in cursor.fetchall()]
  File "/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/core/state_manager.py", line 508, in <listcomp>
    return [self._row_to_task(row) for row in cursor.fetchall()]
  File "/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/core/state_manager.py", line 440, in _row_to_task
    meta = json.loads(row["metadata"] or "{}") if "metadata" in row.keys() else {}
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/json/__init__.py", line 346, in loads
    return _default_decoder.decode(s)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/json/decoder.py", line 337, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/json/decoder.py", line 353, in raw_decode
    obj, end = self.scan_once(s, idx)
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
```

**Additional Corrupt & Scalar Variants Observed**:
1. Scalar JSON integer: `row["metadata"] = "12345"`. `json.loads` returns `12345` (`int`). `TaskRecord.metadata` is typed `Dict[str, Any]`. Downstream code calling `t.metadata.get("difficulty")` crashes with `AttributeError: 'int' object has no attribute 'get'`.
2. Scalar JSON boolean: `row["metadata"] = "true"`. `json.loads` returns `True`. Downstream `t.metadata.get(...)` crashes with `AttributeError: 'bool' object has no attribute 'get'`.
3. Scalar JSON null: `row["metadata"] = "null"`. `json.loads` returns `None`. Downstream `t.metadata.get(...)` crashes with `AttributeError: 'NoneType' object has no attribute 'get'`.
4. Scalar JSON list: `row["metadata"] = "[1, 2, 3]"`. `json.loads` returns `[1, 2, 3]`. Downstream `t.metadata.get(...)` crashes with `AttributeError: 'list' object has no attribute 'get'`.
5. Non-string integer literal in SQLite column: `row["metadata"] = 12345`. `json.loads(12345)` crashes with `TypeError: the JSON object must be str, bytes or bytearray, not int`.
6. HTML error page string: `row["metadata"] = "<!DOCTYPE html>..."`. `json.loads` crashes with `json.decoder.JSONDecodeError`.

---

### 1.2 Defect 2: CLI `run-codekata --difficulty` Crashes with `TypeError` in `main.py`

**File**: `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/main.py`  
**Lines**: 477-488 (in `run-codekata`) and lines 442-448 (in `run-all` `_run_guvi`)  
**Current Implementation**:
```python
# main.py:477-488
pipeline_kwargs = {
    "limit": self.args.limit,
    "category": self.args.category,
    "task_id": self.args.task_id,
}
raw_diff = getattr(self.args, "difficulty", None)
if raw_diff is not None:
    parsed_diffs = parse_difficulties(raw_diff)
    if parsed_diffs:
        pipeline_kwargs["difficulties"] = parsed_diffs

driver.run_pipeline(**pipeline_kwargs)
```
And in `_run_guvi()`:
```python
# main.py:442-448
pipeline_kwargs = {"limit": self.args.limit}
raw_diff = getattr(self.args, "difficulty", None)
if raw_diff is not None:
    parsed_diffs = parse_difficulties(raw_diff)
    if parsed_diffs:
        pipeline_kwargs["difficulties"] = parsed_diffs
guvi_driver.run_pipeline(**pipeline_kwargs)
```

**Target Function Signature in `zenclass_guvi/drivers/guvi_driver.py:867`**:
```python
    def run_pipeline(
        self,
        limit: Optional[int] = None,
        category: Optional[str] = None,
        task_id: Optional[str] = None,
        max_pages: int = 143,
    ) -> Dict[str, Any]:
```
`GuviDriver.run_pipeline` parameter names are: `['self', 'limit', 'category', 'task_id', 'max_pages']`. It has no `difficulties` parameter and no `**kwargs` (`VAR_KEYWORD`).

**Verbatim Reproduction Command**:
```sh
PYTHONPATH=zenclass_guvi python3 -c "
from main import AutomationRunner, create_cli_parser
from unittest.mock import MagicMock

parser = create_cli_parser()
args = parser.parse_args(['run-codekata', '--difficulty', 'Medium'])
runner = AutomationRunner(args)
runner.browser_manager = MagicMock()
runner.state_manager = MagicMock()
runner.hitl_handler = MagicMock()
runner.reporter = MagicMock()
runner.execute()
"
```

**Verbatim Crash Output**:
```
04:36:09 [INFO] zenclass_guvi: Executing CodeKata automation (category=None, limit=None)...
04:36:09 [ERROR] zenclass_guvi: Unhandled error during execution: run_pipeline() got an unexpected keyword argument 'difficulties'
Traceback (most recent call last):
  File "/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/main.py", line 488, in execute
    driver.run_pipeline(**pipeline_kwargs)
TypeError: run_pipeline() got an unexpected keyword argument 'difficulties'
```

---

## 2. Logic Chain

### 2.1 Logic Chain for Defect 1: StateManager Metadata Deserialization

1. **Observation 1.1**: In `core/state_manager.py:487-501`, when `difficulties` contains valid non-empty strings (e.g. `["Medium"]`), the SQL query appends:
   ```sql
   AND CASE 
       WHEN metadata IS NOT NULL AND json_valid(metadata) = 1 
       THEN LOWER(json_extract(metadata, '$.difficulty')) 
       ELSE NULL 
   END IN (?)
   ```
   SQLite's `json_valid(metadata)` filters out unparseable JSON rows at the database engine level.
2. **Observation 1.2**: When `difficulties=None`, `difficulties=[]`, `difficulties=["   "]`, or `difficulties=[None, 123]`, `cleaned_diffs` evaluates to an empty list `[]`. No `json_valid` filter is added to the SQL query.
3. **Observation 1.3**: The database returns all pending rows matching the status filter, including rows with corrupt metadata, raw integers, HTML error strings, or scalar JSON literals.
4. **Observation 1.4**: `list_pending` maps all rows through `self._row_to_task(row)`. Additionally, `get_task`, `list_tasks`, `list_blocked`, and `export_state_json` also invoke `_row_to_task(row)`.
5. **Observation 1.5**: Line 440 executes `meta = json.loads(row["metadata"] or "{}") if "metadata" in row.keys() else {}` without any `try ... except` block and without validating that the decoded JSON is an instance of `dict`.
6. **Inference 1.1**: Any unparseable JSON string raises `json.decoder.JSONDecodeError` (subclass of `ValueError`), halting the entire retrieval pipeline.
7. **Inference 1.2**: Any non-string type (e.g. an integer stored in SQLite) raises `TypeError`, halting the pipeline.
8. **Inference 1.3**: Any valid scalar JSON literal (e.g. `"12345"`, `"true"`, `"null"`, `"[1, 2]"`) successfully parses but yields a non-dict object (`int`, `bool`, `None`, `list`). Downstream code that accesses `task.metadata.get(...)` crashes immediately with `AttributeError`.
9. **Conclusion 1**: `_row_to_task` must encapsulate `json.loads` within a dedicated `try ... except Exception` block AND explicitly verify `isinstance(parsed, dict)`. If parsing fails or the parsed entity is not a `dict`, `meta` must safely default to `{}`.

### 2.2 Logic Chain for Defect 2: CLI Parameter Propagation & Driver Signature Inspection

1. **Observation 2.1**: `PROJECT.md` establishes the interface contract:
   `GuviDriver.run_pipeline(limit=..., category=..., task_id=..., max_pages=..., difficulties=["Medium", "Hard"])`.
2. **Observation 2.2**: `PROJECT.md` and `SCOPE.md` explicitly assign `drivers/guvi_driver.py` to Milestone 3 (Feature 7 & 8), whereas Milestone 1 owns `main.py`, `core/state_manager.py`, `solver/extractor.py`, and `config.py`.
3. **Observation 2.3**: `GuviDriver.run_pipeline` in `zenclass_guvi/drivers/guvi_driver.py:867` currently defines parameters `(self, limit=None, category=None, task_id=None, max_pages=143)` and lacks `difficulties` as well as `**kwargs`.
4. **Observation 2.4**: In `main.py:486` (and `main.py:447`), `pipeline_kwargs["difficulties"] = parsed_diffs` is unconditionally populated whenever `--difficulty` is parsed from the CLI.
5. **Observation 2.5**: When `driver.run_pipeline(**pipeline_kwargs)` is called with `--difficulty Medium`, Python raises `TypeError: run_pipeline() got an unexpected keyword argument 'difficulties'`.
6. **Observation 2.6**: In `tests/test_m1_filtering.py:435`, `test_06_main_runner_wires_difficulty_when_specified` used `@patch("drivers.guvi_driver.GuviDriver.run_pipeline")` with an unconstrained `MagicMock`. Because `inspect.signature(MagicMock())` includes `(*args, **kwargs)`, it accepted `difficulties` without error, masking the signature mismatch against the real driver.
7. **Observation 2.7**: In Python's `inspect` module:
   - For real `GuviDriver.run_pipeline`: `sig.parameters` contains `['limit', 'category', 'task_id', 'max_pages']`. `'difficulties' in sig.parameters` is `False`, and `any(p.kind == inspect.Parameter.VAR_KEYWORD ...)` is `False`.
   - For updated `GuviDriver.run_pipeline` (M3): `'difficulties' in sig.parameters` is `True`.
   - For any driver with `**kwargs`: `any(p.kind == inspect.Parameter.VAR_KEYWORD ...)` is `True`.
   - For an unconstrained `MagicMock` in unit tests: `kwargs` has `kind == Parameter.VAR_KEYWORD`, returning `True`.
8. **Conclusion 2**: `main.py` must inspect `inspect.signature(driver.run_pipeline).parameters` via a robust helper (`supports_parameter`). If `difficulties` is supported (either explicitly or via `**kwargs`), `pipeline_kwargs["difficulties"]` is passed. If not supported, `main.py` must NOT pass `difficulties` in `pipeline_kwargs`, must log an informational message, and must store the parsed difficulties on the driver instance (`setattr(driver, "difficulties", parsed_diffs)`), eliminating the runtime `TypeError`.

---

## 3. Caveats

1. **Milestone Boundary vs Challenger 1 Test Harness Assertion**:
   In `.agents/teamwork/challenger_m1_1/stress_test_harness.py:538-550`, Challenger 1's test 3.4 checks:
   ```python
   sig = inspect.signature(GuviDriver.run_pipeline)
   if "difficulties" in sig.parameters or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
       results.record_pass("CLI GuviDriver Signature Compatibility", ...)
   else:
       results.record_fail("CLI GuviDriver Signature Compatibility", ...)
   ```
   Challenger 1's test 3.4 does not call `main.py` directly; it inspects `GuviDriver.run_pipeline` directly.
   - If the team strictly restricts changes to M1 files (`main.py` and `core/state_manager.py`), `main.py` will never crash on CLI `--difficulty`, but Challenger 1's test 3.4 will report FAIL because it asserts directly on `GuviDriver`.
   - To make both `main.py` crash-proof AND make Challenger 1's test 3.4 PASS immediately, `GuviDriver.run_pipeline` in `drivers/guvi_driver.py:867` should have `difficulties: Optional[List[str]] = None, **kwargs: Any` added to its signature as a forward-compatible interface stub matching the `PROJECT.md` interface contract.
2. **AttemptRecord Details Deserialization at `core/state_manager.py:567`**:
   Line 567 in `get_task_attempts`:
   `details=json.loads(r["details"] or "{}") if "details" in r.keys() else {}`
   While Challenger 1 focused on `_row_to_task:440`, line 567 exhibits the exact same vulnerability if `task_attempts.details` contains malformed JSON or a scalar. We recommend applying the same defensive try-except pattern to line 567.
3. **Mocking in Unit Tests**:
   Unit tests patching `GuviDriver.run_pipeline` with standard `unittest.mock.patch` create an unconstrained mock whose signature contains `**kwargs`. Therefore, existing tests like `test_06` will continue to pass. If tests are migrated to `patch(..., autospec=True)` before `GuviDriver.run_pipeline` signature is updated, they will correctly reflect that the current driver does not accept `difficulties`.

---

## 4. Conclusion & Actionable Recommendations

### 4.1 Recommendation 1: Patch `core/state_manager.py:440` in `_row_to_task`

Replace the naive `json.loads` one-liner with a defensive extraction that:
1. Validates that `row["metadata"]` exists and is non-empty.
2. Accepts existing `dict` objects directly.
3. Catches all exceptions (`json.JSONDecodeError`, `TypeError`, `ValueError`, `Exception`) during `json.loads`.
4. Validates that `isinstance(parsed, dict)` is `True`.
5. Defaults to `{}` in all error or scalar cases.

#### Exact Proposed Code for `zenclass_guvi/core/state_manager.py:439-456`:
```python
    def _row_to_task(self, row: sqlite3.Row) -> TaskRecord:
        meta: Dict[str, Any] = {}
        if "metadata" in row.keys() and row["metadata"]:
            raw_meta = row["metadata"]
            if isinstance(raw_meta, dict):
                meta = raw_meta
            elif isinstance(raw_meta, (str, bytes, bytearray)):
                try:
                    parsed = json.loads(raw_meta)
                    if isinstance(parsed, dict):
                        meta = parsed
                except Exception:
                    meta = {}
            # Non-dict and non-parseable values safely default to empty dict

        return TaskRecord(
            task_id=row["task_id"],
            platform=row["platform"],
            task_category=row["task_category"],
            title=row["title"],
            url=row["url"],
            status=row["status"],
            attempt_count=row["attempt_count"],
            result=row["result"],
            failure_reason=row["failure_reason"],
            next_action=row["next_action"],
            time_spent_seconds=row["time_spent_seconds"],
            metadata=meta,
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
```

#### Complementary Hardening for `zenclass_guvi/core/state_manager.py:567` (`get_task_attempts`):
```python
            results = []
            for r in cursor.fetchall():
                details: Dict[str, Any] = {}
                if "details" in r.keys() and r["details"]:
                    raw_d = r["details"]
                    if isinstance(raw_d, dict):
                        details = raw_d
                    elif isinstance(raw_d, (str, bytes, bytearray)):
                        try:
                            parsed_d = json.loads(raw_d)
                            if isinstance(parsed_d, dict):
                                details = parsed_d
                        except Exception:
                            details = {}

                results.append(AttemptRecord(
                    id=r["id"],
                    task_id=r["task_id"],
                    attempt_number=r["attempt_number"],
                    timestamp=r["timestamp"],
                    status=r["status"],
                    result=r["result"],
                    failure_reason=r["failure_reason"],
                    time_spent_seconds=r["time_spent_seconds"],
                    code_snapshot=r["code_snapshot"] if "code_snapshot" in r.keys() else None,
                    details=details
                ))
```

---

### 4.2 Recommendation 2: Patch `main.py` with `supports_parameter` and Signature Inspection

1. Add `supports_parameter` helper at `main.py` module level (right after `parse_difficulties`).
2. Update `_run_guvi()` in `main.py:442-448` and `run-codekata` in `main.py:482-488` to check if `driver.run_pipeline` supports `"difficulties"`.

#### Exact Proposed Helper for `zenclass_guvi/main.py` (after line 74):
```python
import inspect

def supports_parameter(target_callable: Any, param_name: str) -> bool:
    """
    Inspects whether a function or method accepts the specified parameter name,
    either explicitly in its signature or via variable keyword arguments (**kwargs).
    """
    if not callable(target_callable):
        return False
    try:
        sig = inspect.signature(target_callable)
        params = sig.parameters
        return (
            param_name in params
            or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())
        )
    except (ValueError, TypeError):
        return False
```

#### Exact Proposed Update for `zenclass_guvi/main.py:442-448` (`_run_guvi` in `run-all`):
```python
                def _run_guvi():
                    guvi_driver = GuviDriver(
                        browser_manager=self.browser_manager,
                        state_manager=self.state_manager,
                        hitl_handler=self.hitl_handler,
                        reporter=self.reporter,
                    )
                    pipeline_kwargs = {"limit": self.args.limit}
                    raw_diff = getattr(self.args, "difficulty", None)
                    if raw_diff is not None:
                        parsed_diffs = parse_difficulties(raw_diff)
                        if parsed_diffs:
                            if supports_parameter(guvi_driver.run_pipeline, "difficulties"):
                                pipeline_kwargs["difficulties"] = parsed_diffs
                            else:
                                logger.info(
                                    f"Driver '{guvi_driver.__class__.__name__}.run_pipeline' does not accept "
                                    f"'difficulties' parameter yet; storing on driver instance: {parsed_diffs}"
                                )
                                setattr(guvi_driver, "difficulties", parsed_diffs)
                    guvi_driver.run_pipeline(**pipeline_kwargs)
```

#### Exact Proposed Update for `zenclass_guvi/main.py:482-488` (`run-codekata`):
```python
                pipeline_kwargs = {
                    "limit": self.args.limit,
                    "category": self.args.category,
                    "task_id": self.args.task_id,
                }
                raw_diff = getattr(self.args, "difficulty", None)
                if raw_diff is not None:
                    parsed_diffs = parse_difficulties(raw_diff)
                    if parsed_diffs:
                        if supports_parameter(driver.run_pipeline, "difficulties"):
                            pipeline_kwargs["difficulties"] = parsed_diffs
                        else:
                            logger.info(
                                f"Driver '{driver.__class__.__name__}.run_pipeline' does not accept "
                                f"'difficulties' parameter yet; storing on driver instance: {parsed_diffs}"
                            )
                            setattr(driver, "difficulties", parsed_diffs)

                driver.run_pipeline(**pipeline_kwargs)
```

---

### 4.3 Recommendation 3: Forward-Compatible Signature Stub in `drivers/guvi_driver.py:867`

To fulfill the `PROJECT.md` interface contract (`GuviDriver.run_pipeline(..., difficulties=["Medium", "Hard"])`) and satisfy Challenger 1's test 3.4 assertion, `GuviDriver.run_pipeline` can be updated with non-breaking parameter stubs:

```python
    def run_pipeline(
        self,
        limit: Optional[int] = None,
        category: Optional[str] = None,
        task_id: Optional[str] = None,
        max_pages: int = 143,
        difficulties: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
```
In line 897, it can forward `difficulties` to `state_manager.list_pending`:
```python
            existing_pending = (
                self.state_manager.list_pending(platform="guvi", limit=limit, difficulties=difficulties)
                if self.state_manager
                else []
            )
```

---

## 5. Verification Method

### 5.1 Independent Reproduction & Verification Commands

1. **Verify Defect 1 Resolution (Corrupt & Scalar Metadata in StateManager)**:
   ```sh
   PYTHONPATH=zenclass_guvi python3 -c "
   import sqlite3, tempfile
   from pathlib import Path
   from core.state_manager import StateManager

   with tempfile.TemporaryDirectory() as tmp:
       db = Path(tmp) / 'corrupt.db'
       sm = StateManager(db_path=str(db))
       conn = sqlite3.connect(str(db))
       test_cases = [
           ('c-1', '{corrupt json'),
           ('c-2', '12345'),
           ('c-3', 'true'),
           ('c-4', 'null'),
           ('c-5', '\"scalar string\"'),
           ('c-6', '[1, 2, 3]'),
           ('c-7', ''),
           ('c-8', None),
           ('v-1', '{\"difficulty\": \"Medium\"}')
       ]
       for tid, meta in test_cases:
           conn.execute('''
               INSERT INTO tasks (task_id, platform, task_category, title, status, metadata, created_at, updated_at)
               VALUES (?, 'guvi', 'Basics', 'Test', 'pending', ?, '2026-01-01', '2026-01-01')
           ''', (tid, meta))
       conn.commit()
       conn.close()

       tasks = sm.list_pending(difficulties=None)
       assert len(tasks) == 9, f'Expected 9 tasks, got {len(tasks)}'
       for t in tasks:
           assert isinstance(t.metadata, dict), f'Task {t.task_id} metadata is not dict'
           t.metadata.get('difficulty')

       # Whitespace difficulty query
       ws_tasks = sm.list_pending(difficulties=['   ', '  \t '])
       assert len(ws_tasks) == 9

       # Filtered query
       med_tasks = sm.list_pending(difficulties=['Medium'])
       assert len(med_tasks) == 1
       assert med_tasks[0].task_id == 'v-1'
       print('Defect 1 verification PASSED.')
   "
   ```

2. **Verify Defect 2 Resolution (CLI `--difficulty` against Real/Mock Drivers)**:
   ```sh
   PYTHONPATH=zenclass_guvi python3 -c "
   from main import AutomationRunner, create_cli_parser
   from unittest.mock import MagicMock

   parser = create_cli_parser()
   args = parser.parse_args(['run-codekata', '--difficulty', 'Medium'])
   runner = AutomationRunner(args)
   runner.browser_manager = MagicMock()
   runner.state_manager = MagicMock()
   runner.hitl_handler = MagicMock()
   runner.reporter = MagicMock()
   exit_code = runner.execute()
   assert exit_code == 0, f'Expected exit code 0, got {exit_code}'
   print('Defect 2 verification PASSED.')
   "
   ```

3. **Verify Standard Test Suite**:
   ```sh
   cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
   python3 -m pytest tests/test_m1_filtering.py
   ```

4. **Verify Challenger Stress Test Harness**:
   ```sh
   cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
   python3 /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/challenger_m1_1/stress_test_harness.py
   ```

### 5.2 Invalidation Conditions
- Defect 1 is INVALIDATED if `list_pending(difficulties=None)` raises `json.decoder.JSONDecodeError` or `TypeError` when any corrupt row is in SQLite, or if `task.metadata` is ever a non-dict type.
- Defect 2 is INVALIDATED if `zenclass_guvi run-codekata --difficulty Medium` or `zenclass_guvi run-all --difficulty Medium` raises `TypeError: run_pipeline() got an unexpected keyword argument 'difficulties'`.
