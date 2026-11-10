# Handoff Report: Explorer 3 — CLI & Configuration Foundation (Milestone 1)

**Target Scope**: `config.py`, `main.py`, CLI commands (`run-codekata`, `run-all`, `resume`), `--headless`/`--no-headless` flags, `--difficulty` option handling, and regression verification.  
**Author**: Explorer 3  
**Date**: 2026-11-10T22:35:00Z  

---

## 1. Observation

### 1.1 `config.py` Current Headless & Difficulty Configuration
- **File**: `zenclass_guvi/config.py` (lines 49–54, 108):
  ```python
  # Browser Execution Settings (Requirement R1: visible foreground browser)
  HEADLESS = os.getenv("AUTOMATION_HEADLESS", "false").lower() == "true"  # strictly False by default
  SLOW_MO = float(os.getenv("AUTOMATION_SLOW_MO", "50.0"))  # 50ms realistic human cadence
  NAVIGATION_TIMEOUT = float(os.getenv("AUTOMATION_NAV_TIMEOUT", "30000.0"))  # 30 seconds
  DEFAULT_TIMEOUT = float(os.getenv("AUTOMATION_TIMEOUT", "10000.0"))  # 10 seconds
  ...
  class Config:
      ...
      HEADLESS = HEADLESS
  ```
- **Observations**:
  1. `config.HEADLESS` strictly evaluates to `False` unless environment variable `AUTOMATION_HEADLESS` is explicitly set to `"true"`.
  2. There are no difficulty constants (such as `DEFAULT_CODEKATA_DIFFICULTIES` or `VALID_CODEKATA_DIFFICULTIES`) anywhere in `config.py`.

### 1.2 `core/browser.py` Headless Resolution
- **File**: `zenclass_guvi/core/browser.py` (lines 53–59):
  ```python
  def __init__(
      self,
      profile_dir: Optional[Path] = None,
      storage_state_path: Optional[Path] = None,
      headless: Optional[bool] = None,
      slow_mo: Optional[float] = None,
      navigation_timeout: Optional[float] = None,
      default_timeout: Optional[float] = None,
  ):
      ...
      self.headless = config.HEADLESS if headless is None else headless
  ```
- **Observation**:
  `BrowserManager` defaults its `self.headless` attribute directly from `config.HEADLESS` when the parameter `headless is None`. If `headless` is explicitly passed (e.g. `False` from CLI default), it overrides `config.HEADLESS`.

### 1.3 `main.py` CLI Parser Architecture and Limitations
- **File**: `zenclass_guvi/main.py` (lines 48–53, 118–135):
  ```python
  # Global options on root parser
  parser.add_argument(
      "--headless",
      action="store_true",
      default=False,
      help="Run browser in headless mode (default: False, headed foreground as per R1)",
  )
  ...
  # Command: run-codekata
  p_codekata = subparsers.add_parser(
      "run-codekata",
      help="Run Guvi CodeKata automation (discovery, solver, sandbox, submission)",
  )
  p_codekata.add_argument(
      "--category",
      type=str,
      default=None,
      help="Filter CodeKata problems by category/topic (e.g., 'Basics', 'Strings')",
  )
  p_codekata.add_argument(
      "--task-id",
      type=str,
      default=None,
      help="Execute single CodeKata problem by slug or title",
  )
  ```
- **File**: `zenclass_guvi/main.py` (lines 255–264, 362–376):
  ```python
  def initialize_browser(self) -> None:
      """Launches persistent headed browser session."""
      logger.info(
          f"Launching browser session (headless={self.args.headless}, slow_mo={self.args.slow_mo}ms)..."
      )
      self.browser_manager = BrowserManager(
          headless=self.args.headless,
          slow_mo=self.args.slow_mo
      )
      self.browser_manager.start()
  ...
  elif self.args.command == "run-codekata":
      logger.info(f"Executing CodeKata automation (category={self.args.category}, limit={self.args.limit})...")
      from drivers.guvi_driver import GuviDriver
      driver = GuviDriver(
          browser_manager=self.browser_manager,
          state_manager=self.state_manager,
          hitl_handler=self.hitl_handler,
          reporter=self.reporter,
      )
      driver.run_pipeline(
          limit=self.args.limit,
          category=self.args.category,
          task_id=self.args.task_id,
      )
  ```
- **Observations**:
  1. `main.py` uses standard library `argparse`.
  2. `--headless` is defined only on the root `parser` with `default=False`. Because `AutomationRunner.initialize_browser()` unconditionally passes `headless=self.args.headless` into `BrowserManager`, `BrowserManager` always receives `headless=False` unless `--headless` is provided on the command line.
  3. Because `--headless` is defined solely on the root parser before `subparsers`, placing `--headless` after a subcommand (e.g. `python main.py run-codekata --headless`) triggers a verbatim argparse error:
     ```
     zenclass_guvi: error: unrecognized arguments: --headless
     ```
  4. There is no `--no-headless` or `--headed` flag. If the default is switched to `True`, users currently have no flag to request headed execution.
  5. `--difficulty` is completely absent from `main.py`. It is not defined in `create_cli_parser()` and not passed to `GuviDriver.run_pipeline()`.

### 1.4 Interface Contracts & Regression Baseline
- **Existing Test Execution**:
  Command: `PYTHONPATH=zenclass_guvi python3 -m unittest discover -s zenclass_guvi/tests`
  Result:
  ```
  Ran 268 tests in 69.297s
  OK
  ```
  All 268 existing unit, integration, and E2E tests currently pass.
- **Legacy Tests Checking `config.HEADLESS`**:
  1. `zenclass_guvi/tests/test_m1_core.py:44-50`:
     ```python
     def test_default_headed_mode(self):
         """Authoritative source: ORIGINAL_REQUEST §R1 & PROJECT.md: headless=False."""
         self.assertFalse(
             config.HEADLESS,
             "Browser execution MUST default to headless=False for foreground visual monitoring."
         )
     ```
  2. `zenclass_guvi/tests/empirical_challenge_m3_iter2.py:379-385`:
     ```python
     def test_09_anti_detection_flags_and_headed_mode_configuration(self):
         """Verify configuration enforces headed execution (R1) and anti-detection flags."""
         self.assertFalse(config.HEADLESS, "Requirement R1 strictly requires headed foreground execution (HEADLESS=False)")
     ```
- **Test Checking CLI `run-codekata` Mock Invocations**:
  - `zenclass_guvi/tests/test_m3_guvi.py:841-857`:
    ```python
    @patch("drivers.guvi_driver.GuviDriver.run_pipeline")
    def test_main_cli_wires_run_codekata(self, mock_run_pipeline):
        """Verifies 'run-codekata' command properly invokes GuviDriver.run_pipeline()."""
        parser = create_cli_parser()
        args = parser.parse_args(["--limit", "3", "run-codekata", "--category", "Basics"])
        runner = AutomationRunner(args)
        ...
        exit_code = runner.execute()
        self.assertEqual(exit_code, 0)
        mock_run_pipeline.assert_called_once_with(limit=3, category="Basics", task_id=None)
    ```
  - **Critical Finding**: If `main.py` passes `difficulties=...` to `driver.run_pipeline()` when `--difficulty` was not provided on the CLI, `mock_run_pipeline.assert_called_once_with(limit=3, category="Basics", task_id=None)` fails with an `AssertionError`.
  - Furthermore, `GuviDriver.run_pipeline()` in `zenclass_guvi/drivers/guvi_driver.py:867` (owned by M3) currently has the signature:
    `def run_pipeline(self, limit: Optional[int] = None, category: Optional[str] = None, task_id: Optional[str] = None, max_pages: int = 143) -> Dict[str, Any]:`
    If `main.py` unconditionally passes `difficulties=...` before M3 updates `guvi_driver.py`, calling `run_pipeline` will raise a runtime `TypeError`.

---

## 2. Logic Chain

1. **Requirement Evolution (Observation 1.1 vs Follow-up R1)**:
   The original user prompt required headed foreground execution (`headless=False`). The follow-up request (2026-11-10T22:13:52Z) explicitly redefines R1: *"Filter and solve all Medium and Hard difficulty practice questions on Guvi CodeKata in headless background mode using Python, verifying solutions against platform test cases and persisting execution state."*
   Therefore, the default execution mode across configuration and CLI must become headless background execution (`headless=True`), while retaining configurable headed override.

2. **Configuration Defaulting in `config.py`**:
   Changing `config.HEADLESS` default requires setting:
   `HEADLESS = os.getenv("AUTOMATION_HEADLESS", "true").lower() in ("true", "1", "yes")`
   This makes background headless execution the default when no environment variable is set, while allowing users to set `AUTOMATION_HEADLESS=false` or `0` for headed execution.
   Additionally, adding constants `DEFAULT_CODEKATA_DIFFICULTIES = ["Medium", "Hard"]` and `VALID_CODEKATA_DIFFICULTIES = ["Easy", "Medium", "Hard"]` centralizes domain knowledge in `config.py`.

3. **Subparser Flag Placement in `main.py` (Observation 1.3)**:
   Because users naturally type both `python main.py --headless run-codekata` and `python main.py run-codekata --headless`, defining flags solely on the root parser causes `argparse` syntax errors for the latter.
   By defining a `shared_sub` parser with `default=argparse.SUPPRESS` for `--headless`, `--no-headless`, and `--headed`, and inheriting `parents=[shared_sub]` on subparsers (`p_codekata`, `p_run_all`, etc.):
   - The root parser establishes the default: `default=config.HEADLESS` (True).
   - The subparser does NOT clobber the namespace when flags are omitted or placed before the subcommand.
   - The subparser correctly captures flags when placed after the subcommand (`run-codekata --no-headless` or `run-codekata --headed`).

4. **Difficulty Parsing Strategy (`--difficulty`)**:
   Users and automation scripts may specify difficulty in multiple ways:
   - Comma-separated: `--difficulty Medium,Hard` or `--difficulty "Medium, Hard"`
   - Repeated options: `--difficulty Medium --difficulty Hard`
   - Single option: `--difficulty Hard`
   - Case variations: `--difficulty medium,hard`
   Using `action="append"` in `argparse` combined with a normalization helper `parse_difficulties()`:
   - Flattens strings or lists of strings.
   - Splits on commas and strips whitespace.
   - Capitalizes to Title Case (`"medium"` $\to$ `"Medium"`, `"hard"` $\to$ `"Hard"`).
   - Validates against `config.VALID_CODEKATA_DIFFICULTIES` (`["Easy", "Medium", "Hard"]`).
   - Deduplicates preserving order.

5. **Driver Propagation & Backward Compatibility (Observation 1.4)**:
   In `AutomationRunner.execute()`:
   - If `--difficulty` is specified, `parse_difficulties(self.args.difficulty)` produces e.g. `["Medium", "Hard"]`.
   - To preserve backward compatibility with `test_m3_guvi.py:856` and avoid breaking before M3 modifies `GuviDriver.run_pipeline`, `main.py` should only include `"difficulties"` in `pipeline_kwargs` when `--difficulty` was explicitly passed or when inspected parameters show `difficulties` support.
   - When `--difficulty` is omitted on the CLI, `driver.run_pipeline` will apply its own default `["Medium", "Hard"]` once updated in M3, satisfying `PROJECT.md` line 59: `GuviDriver.run_pipeline(..., difficulties=["Medium", "Hard"])`.

---

## 3. Caveats

1. **Legacy Test Assertions**:
   `test_m1_core.py:46` and `empirical_challenge_m3_iter2.py:381` explicitly test the obsolete initial requirement `self.assertFalse(config.HEADLESS)`. If `config.HEADLESS` default is changed to `True`, these two tests will fail unless either:
   - They are updated to assert `self.assertTrue(config.HEADLESS)` (matching the Follow-up R1 requirement), OR
   - The test environment sets `AUTOMATION_HEADLESS=false` when running legacy suites.
   Updating the assertion to reflect the user's latest follow-up requirement is recommended.
2. **Sub-Milestone Independence**:
   `GuviDriver` is owned by Milestone 3. Milestone 1 implementers must NOT edit `drivers/guvi_driver.py`. The wiring in `main.py` must use conditional/kwargs propagation so existing tests pass without waiting for M3.

---

## 4. Conclusion

### 4.1 Recommended Changes to `zenclass_guvi/config.py`
```python
# --- Browser Execution Settings (Requirement R1: Background Headless Execution) ---
HEADLESS = os.getenv("AUTOMATION_HEADLESS", "true").lower() in ("true", "1", "yes")
SLOW_MO = float(os.getenv("AUTOMATION_SLOW_MO", "50.0"))
NAVIGATION_TIMEOUT = float(os.getenv("AUTOMATION_NAV_TIMEOUT", "30000.0"))
DEFAULT_TIMEOUT = float(os.getenv("AUTOMATION_TIMEOUT", "10000.0"))

# --- CodeKata Difficulty Settings ---
DEFAULT_CODEKATA_DIFFICULTIES = ["Medium", "Hard"]
VALID_CODEKATA_DIFFICULTIES = ["Easy", "Medium", "Hard"]

class Config:
    ...
    HEADLESS = HEADLESS
    DEFAULT_CODEKATA_DIFFICULTIES = DEFAULT_CODEKATA_DIFFICULTIES
    VALID_CODEKATA_DIFFICULTIES = VALID_CODEKATA_DIFFICULTIES
```

### 4.2 Recommended Changes to `zenclass_guvi/main.py`

#### A. Parsing Helper Function
```python
def parse_difficulties(raw_diff: Union[str, List[str], None]) -> Optional[List[str]]:
    """
    Parses comma-separated strings or repeated flags into normalized Title Case difficulty list.
    Supports:
      - ['Medium,Hard'] -> ['Medium', 'Hard']
      - ['Medium', 'Hard'] -> ['Medium', 'Hard']
      - 'medium, hard' -> ['Medium', 'Hard']
      - 'Hard' -> ['Hard']
    """
    if not raw_diff:
        return None
    raw_list = [raw_diff] if isinstance(raw_diff, str) else raw_diff
    result = []
    for item in raw_list:
        for part in item.split(","):
            token = part.strip().capitalize()
            if token and token in config.VALID_CODEKATA_DIFFICULTIES:
                if token not in result:
                    result.append(token)
            elif token:
                logger.warning(f"Unrecognized difficulty level: '{part.strip()}'. Ignored.")
    return result or None
```

#### B. CLI Parser Enhancements (`create_cli_parser`)
```python
def create_cli_parser() -> argparse.ArgumentParser:
    ...
    # Shared subparser for options allowed both globally and after subcommands
    shared_browser = argparse.ArgumentParser(add_help=False)
    shared_browser.add_argument(
        "--headless",
        dest="headless",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Run browser in background headless mode",
    )
    shared_browser.add_argument(
        "--no-headless",
        dest="headless",
        action="store_false",
        default=argparse.SUPPRESS,
        help="Run browser in visible foreground headed mode",
    )
    shared_browser.add_argument(
        "--headed",
        dest="headless",
        action="store_false",
        default=argparse.SUPPRESS,
        help="Alias for --no-headless: run browser in visible foreground headed mode",
    )

    # Root parser options
    parser.add_argument(
        "--headless",
        dest="headless",
        action="store_true",
        default=config.HEADLESS,
        help="Run browser in background headless mode (default: True, per R1 follow-up)",
    )
    parser.add_argument(
        "--no-headless",
        dest="headless",
        action="store_false",
        help="Run browser in visible foreground headed mode",
    )
    parser.add_argument(
        "--headed",
        dest="headless",
        action="store_false",
        help="Alias for --no-headless: run browser in visible foreground headed mode",
    )
    ...
    # Subcommand: run-codekata
    p_codekata = subparsers.add_parser(
        "run-codekata",
        parents=[shared_browser],
        help="Run Guvi CodeKata automation (discovery, solver, sandbox, submission)",
    )
    p_codekata.add_argument(
        "--difficulty",
        action="append",
        default=None,
        help="Filter CodeKata problems by difficulty (e.g., '--difficulty Medium,Hard' or '--difficulty Medium --difficulty Hard'). Allowed: Easy, Medium, Hard",
    )
    ...
    # Subcommand: run-all (also benefits from shared_browser and optional difficulty)
    p_run_all = subparsers.add_parser(
        "run-all",
        parents=[shared_browser],
        help="Run full automation pipeline across Guvi CodeKata, ZenClass tasks, and projects",
    )
    p_run_all.add_argument(
        "--difficulty",
        action="append",
        default=None,
        help="Filter CodeKata problems by difficulty within run-all",
    )
```

#### C. Runner Invocation in `AutomationRunner.execute()`
```python
            elif self.args.command == "run-codekata":
                logger.info(f"Executing CodeKata automation (category={self.args.category}, limit={self.args.limit})...")
                from drivers.guvi_driver import GuviDriver
                driver = GuviDriver(
                    browser_manager=self.browser_manager,
                    state_manager=self.state_manager,
                    hitl_handler=self.hitl_handler,
                    reporter=self.reporter,
                )
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

---

## 5. Verification Method

To verify these changes independently:

1. **Verify Headless Defaults**:
   ```bash
   PYTHONPATH=zenclass_guvi python3 -c "
   import config
   from main import create_cli_parser
   assert config.HEADLESS is True
   p = create_cli_parser()
   assert p.parse_args(['run-codekata']).headless is True
   assert p.parse_args(['--no-headless', 'run-codekata']).headless is False
   assert p.parse_args(['run-codekata', '--no-headless']).headless is False
   assert p.parse_args(['run-codekata', '--headed']).headless is False
   assert p.parse_args(['run-codekata', '--headless']).headless is True
   print('Headless flag verification passed!')
   "
   ```

2. **Verify Difficulty Option Parsing**:
   ```bash
   PYTHONPATH=zenclass_guvi python3 -c "
   from main import create_cli_parser, parse_difficulties
   p = create_cli_parser()

   # Comma separated
   args1 = p.parse_args(['run-codekata', '--difficulty', 'Medium,Hard'])
   assert parse_difficulties(args1.difficulty) == ['Medium', 'Hard']

   # Repeated flags
   args2 = p.parse_args(['run-codekata', '--difficulty', 'Medium', '--difficulty', 'Hard'])
   assert parse_difficulties(args2.difficulty) == ['Medium', 'Hard']

   # Case insensitive & spaces
   args3 = p.parse_args(['run-codekata', '--difficulty', '  medium , hard  '])
   assert parse_difficulties(args3.difficulty) == ['Medium', 'Hard']

   # Default (omitted)
   args4 = p.parse_args(['run-codekata'])
   assert args4.difficulty is None

   print('Difficulty parsing verification passed!')
   "
   ```

3. **Verify Existing 268 Tests & New M1 Filtering Suite**:
   ```bash
   PYTHONPATH=zenclass_guvi python3 -m unittest discover -s zenclass_guvi/tests
   ```
   *Invalidation condition*: Any failure in `test_m1_core.py`, `test_m3_guvi.py`, or `test_m1_filtering.py`.
