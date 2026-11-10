"""
Milestone 1 Challenger Stress Test Harness
Adversarial testing for:
1. core/state_manager.py: 1,000 synthetic tasks, corrupt metadata, SQL injection, concurrency.
2. main.py: CLI argument parser, flag ordering, difficulty normalization.
3. solver/extractor.py: CSS sanitization edge cases.
"""

import sys
import os
import json
import sqlite3
import threading
import tempfile
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path("/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from core.state_manager import StateManager, TaskRecord, TaskStatus, TaskPlatform
from main import create_cli_parser, parse_difficulties
from solver.extractor import ProblemExtractor


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def record_pass(self, test_name: str, detail: str = ""):
        self.passed += 1
        print(f"  [PASS] {test_name} {detail}")

    def record_fail(self, test_name: str, reason: str):
        self.failed += 1
        self.errors.append((test_name, reason))
        print(f"  [FAIL] {test_name}: {reason}")


def test_1000_synthetic_tasks(results: TestResults):
    print("\n--- TEST SUITE 1: 1,000 Synthetic Tasks & StateManager Stress ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "stress_state.db"
        json_path = Path(tmpdir) / "stress_state.json"
        sm = StateManager(db_path=str(db_path), json_export_path=str(json_path))

        # Direct SQLite connection to inject corrupt/raw metadata
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Categorized counters
        expected_counts = {
            "easy": 0,
            "medium": 0,
            "hard": 0,
            "sql_injection_match": 0,
            "corrupt_metadata": 0,
            "null_metadata": 0,
            "empty_metadata": 0,
            "missing_difficulty": 0,
            "numeric_difficulty": 0,
            "unicode_difficulty": 0,
        }

        tasks_to_insert = []
        now = "2026-11-10T22:00:00Z"

        # 1. 50 tasks with NULL metadata
        for i in range(50):
            t_id = f"task-null-{i:03d}"
            tasks_to_insert.append((t_id, "guvi_codekata", "Basics", f"Null Task {i}", "", "PENDING", 0, "", None, "", 0.0, None, now, now))
            expected_counts["null_metadata"] += 1

        # 2. 50 tasks with empty string metadata
        for i in range(50):
            t_id = f"task-empty-{i:03d}"
            tasks_to_insert.append((t_id, "guvi_codekata", "Basics", f"Empty Task {i}", "", "PENDING", 0, "", None, "", 0.0, "", now, now))
            expected_counts["empty_metadata"] += 1

        # 3. 50 tasks with corrupt JSON string in metadata
        corrupt_samples = [
            "{corrupt json",
            "not a json object",
            '{"unclosed_key": ',
            '{"key": undefined}',
            "{'single_quotes': True}",
            "<!DOCTYPE html><html><body>Error</body></html>",
            "[1, 2, 3,",
            "null",  # valid JSON literal null string
            "true",  # valid JSON boolean literal
            "12345", # valid JSON integer literal
        ]
        for i in range(50):
            t_id = f"task-corrupt-{i:03d}"
            raw_meta = corrupt_samples[i % len(corrupt_samples)]
            tasks_to_insert.append((t_id, "guvi_codekata", "Basics", f"Corrupt Task {i}", "", "PENDING", 0, "", None, "", 0.0, raw_meta, now, now))
            expected_counts["corrupt_metadata"] += 1

        # 4. 100 tasks with valid JSON but missing 'difficulty'
        for i in range(100):
            t_id = f"task-nodiff-{i:03d}"
            meta = json.dumps({"category": "Basics", "tags": ["math", "array"], "score": i})
            tasks_to_insert.append((t_id, "guvi_codekata", "Basics", f"NoDiff Task {i}", "", "PENDING", 0, "", None, "", 0.0, meta, now, now))
            expected_counts["missing_difficulty"] += 1

        # 5. 50 tasks with integer / float / numeric difficulty
        numeric_diffs = [42, 0, -1, 100, 3.1415, 99999]
        for i in range(50):
            t_id = f"task-numeric-{i:03d}"
            diff_val = numeric_diffs[i % len(numeric_diffs)]
            meta = json.dumps({"difficulty": diff_val, "note": "numeric difficulty"})
            tasks_to_insert.append((t_id, "guvi_codekata", "Basics", f"Numeric Task {i}", "", "PENDING", 0, "", None, "", 0.0, meta, now, now))
            expected_counts["numeric_difficulty"] += 1

        # 6. 50 tasks with non-string / nested difficulty (list, dict, bool)
        nested_diffs = [True, False, None, ["medium"], {"level": "hard"}, ["Easy", "Hard"]]
        for i in range(50):
            t_id = f"task-nested-{i:03d}"
            diff_val = nested_diffs[i % len(nested_diffs)]
            meta = json.dumps({"difficulty": diff_val})
            tasks_to_insert.append((t_id, "guvi_codekata", "Basics", f"Nested Task {i}", "", "PENDING", 0, "", None, "", 0.0, meta, now, now))

        # 7. 200 tasks with mixed-case and whitespace difficulties
        # (50 lowercase "medium", 50 uppercase "HARD", 50 mixed "eAsY", 50 padded "  hard  ")
        for i in range(50):
            t_id = f"task-med-lower-{i:03d}"
            meta = json.dumps({"difficulty": "medium", "index": i})
            tasks_to_insert.append((t_id, "guvi_codekata", "Basics", f"Med Lower Task {i}", "", "PENDING", 0, "", None, "", 0.0, meta, now, now))
            expected_counts["medium"] += 1

        for i in range(50):
            t_id = f"task-hard-upper-{i:03d}"
            meta = json.dumps({"difficulty": "HARD", "index": i})
            tasks_to_insert.append((t_id, "guvi_codekata", "Basics", f"Hard Upper Task {i}", "", "PENDING", 0, "", None, "", 0.0, meta, now, now))
            expected_counts["hard"] += 1

        for i in range(50):
            t_id = f"task-easy-mixed-{i:03d}"
            meta = json.dumps({"difficulty": "eAsY", "index": i})
            tasks_to_insert.append((t_id, "guvi_codekata", "Basics", f"Easy Mixed Task {i}", "", "PENDING", 0, "", None, "", 0.0, meta, now, now))
            expected_counts["easy"] += 1

        for i in range(50):
            t_id = f"task-hard-padded-{i:03d}"
            # Note: in DB string has leading/trailing spaces
            meta = json.dumps({"difficulty": "  hard  ", "index": i})
            tasks_to_insert.append((t_id, "guvi_codekata", "Basics", f"Hard Padded Task {i}", "", "PENDING", 0, "", None, "", 0.0, meta, now, now))
            # We will test whether whitespace in DB is stripped or exact

        # 8. 50 tasks with unicode difficulties
        unicode_diffs = ["Mëdïüm", "🔥", "難易度", "Hard\u0000", "مرحبا"]
        for i in range(50):
            t_id = f"task-unicode-{i:03d}"
            u_diff = unicode_diffs[i % len(unicode_diffs)]
            meta = json.dumps({"difficulty": u_diff})
            tasks_to_insert.append((t_id, "guvi_codekata", "Basics", f"Unicode Task {i}", "", "PENDING", 0, "", None, "", 0.0, meta, now, now))
            expected_counts["unicode_difficulty"] += 1

        # 9. 50 tasks with SQL injection attempts in difficulty value
        sqli_diffs = [
            "'; DROP TABLE tasks; --",
            "' OR 1=1 --",
            "Medium' UNION SELECT * FROM tasks --",
            "1; SELECT 1;",
            "x' AND 1=0 UNION ALL SELECT 1,2,3,4,5,6,7,8,9,10,11,12,13,14 --"
        ]
        for i in range(50):
            t_id = f"task-sqli-{i:03d}"
            s_diff = sqli_diffs[i % len(sqli_diffs)]
            meta = json.dumps({"difficulty": s_diff})
            tasks_to_insert.append((t_id, "guvi_codekata", "Basics", f"SQLi Task {i}", "", "PENDING", 0, "", None, "", 0.0, meta, now, now))

        # 10. 100 standard Easy tasks
        for i in range(100):
            t_id = f"task-easy-std-{i:03d}"
            meta = json.dumps({"difficulty": "Easy", "index": i})
            tasks_to_insert.append((t_id, "guvi_codekata", "Basics", f"Easy Std Task {i}", "", "PENDING", 0, "", None, "", 0.0, meta, now, now))
            expected_counts["easy"] += 1

        # 11. 125 standard Medium tasks
        for i in range(125):
            t_id = f"task-med-std-{i:03d}"
            meta = json.dumps({"difficulty": "Medium", "index": i})
            tasks_to_insert.append((t_id, "guvi_codekata", "Basics", f"Med Std Task {i}", "", "PENDING", 0, "", None, "", 0.0, meta, now, now))
            expected_counts["medium"] += 1

        # 12. 125 standard Hard tasks
        for i in range(125):
            t_id = f"task-hard-std-{i:03d}"
            meta = json.dumps({"difficulty": "Hard", "index": i})
            tasks_to_insert.append((t_id, "guvi_codekata", "Basics", f"Hard Std Task {i}", "", "PENDING", 0, "", None, "", 0.0, meta, now, now))
            expected_counts["hard"] += 1

        # Total tasks check
        assert len(tasks_to_insert) == 1000, f"Total generated tasks {len(tasks_to_insert)} != 1000"

        # Bulk insert directly into SQLite
        cursor.executemany("""
        INSERT INTO tasks (
            task_id, platform, task_category, title, url, status,
            attempt_count, result, failure_reason, next_action,
            time_spent_seconds, metadata, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tasks_to_insert)
        conn.commit()
        conn.close()

        # Verify DB has exactly 1,000 tasks
        with sm._lock:
            c = sm.conn.cursor()
            c.execute("SELECT count(*) FROM tasks;")
            db_count = c.fetchone()[0]
        if db_count == 1000:
            results.record_pass("DB Population", "1,000 synthetic tasks inserted successfully")
        else:
            results.record_fail("DB Population", f"DB has {db_count} rows, expected 1000")

        # Challenge 1.1: Query with single difficulty 'Medium'
        try:
            med_tasks = sm.list_pending(difficulties=["Medium"])
            if len(med_tasks) == expected_counts["medium"]:
                results.record_pass("Filter 'Medium'", f"Found exactly {len(med_tasks)} tasks (expected {expected_counts['medium']})")
            else:
                results.record_fail("Filter 'Medium'", f"Found {len(med_tasks)}, expected {expected_counts['medium']}")
        except Exception as e:
            results.record_fail("Filter 'Medium'", f"Exception: {e}")

        # Challenge 1.2: Query with mixed-case ['medium', 'HARD']
        try:
            med_hard_tasks = sm.list_pending(difficulties=["medium", "HARD"])
            expected_med_hard = expected_counts["medium"] + expected_counts["hard"]
            if len(med_hard_tasks) == expected_med_hard:
                results.record_pass("Filter ['medium', 'HARD']", f"Found exactly {len(med_hard_tasks)} tasks (expected {expected_med_hard})")
            else:
                results.record_fail("Filter ['medium', 'HARD']", f"Found {len(med_hard_tasks)}, expected {expected_med_hard}")
        except Exception as e:
            results.record_fail("Filter ['medium', 'HARD']", f"Exception: {e}")

        # Challenge 1.3: SQL Injection attempts in difficulties query parameter
        sqli_tests = [
            "'; DROP TABLE tasks; --",
            "' OR 1=1 --",
            "Medium' UNION SELECT * FROM tasks --",
            "1; SELECT 1;",
            "x' AND 1=0 UNION ALL SELECT 1,2,3,4,5,6,7,8,9,10,11,12,13,14 --"
        ]
        try:
            res_sqli = sm.list_pending(difficulties=sqli_tests)
            # Check table still exists and intact
            with sm._lock:
                c = sm.conn.cursor()
                c.execute("SELECT count(*) FROM tasks;")
                remaining = c.fetchone()[0]
            if remaining == 1000:
                results.record_pass("SQL Injection Defense (Integrity)", f"Table intact with {remaining} rows after malicious injection queries")
            else:
                results.record_fail("SQL Injection Defense (Integrity)", f"Table corrupted or dropped! Remaining rows: {remaining}")
            
            # Tasks matching SQL injection strings in DB metadata
            if len(res_sqli) == 50:
                results.record_pass("SQL Injection Match (Exact Param)", f"Correctly retrieved exactly {len(res_sqli)} tasks having injection strings as metadata")
            else:
                results.record_fail("SQL Injection Match (Exact Param)", f"Retrieved {len(res_sqli)} tasks, expected 50")
        except Exception as e:
            results.record_fail("SQL Injection Defense", f"Exception: {e}")

        # Challenge 1.4: Query with whitespace difficulties in parameter
        try:
            whitespace_res = sm.list_pending(difficulties=["   ", "\t\n  "])
            # Should ignore whitespace difficulties and return all pending tasks or handle gracefully
            # Note: if cleaned_diffs is empty, list_pending doesn't filter by difficulty
            # BUT: wait, if it returns all tasks, does _row_to_task fail on corrupt metadata?
            # Let's test!
            results.record_pass("Whitespace Difficulties Query", f"Returned {len(whitespace_res)} tasks without crash")
        except Exception as e:
            results.record_fail("Whitespace Difficulties Query", f"Crashed on whitespace difficulties: {e}")

        # Challenge 1.5: Query with corrupt metadata in table - does list_pending with difficulties crash?
        try:
            all_diffs_res = sm.list_pending(difficulties=["Easy", "Medium", "Hard"])
            # Corrupt metadata rows should be skipped by the JSON check and NOT cause an error
            expected_total = expected_counts["easy"] + expected_counts["medium"] + expected_counts["hard"]
            if len(all_diffs_res) == expected_total:
                results.record_pass("Corrupt Metadata Skip in Filtered Query", f"Retrieved {len(all_diffs_res)} tasks without crash (corrupt rows safely ignored)")
            else:
                results.record_fail("Corrupt Metadata Skip in Filtered Query", f"Retrieved {len(all_diffs_res)}, expected {expected_total}")
        except Exception as e:
            results.record_fail("Corrupt Metadata Skip in Filtered Query", f"Crashed on corrupt metadata: {e}")

        # Challenge 1.6: Query with non-string types in difficulties list
        try:
            res_mixed_types = sm.list_pending(difficulties=[None, 123, True, [], {}])  # type: ignore
            results.record_pass("Non-string Types in Difficulties", f"Handled non-string types gracefully, returned {len(res_mixed_types)} tasks")
        except Exception as e:
            results.record_fail("Non-string Types in Difficulties", f"Crashed on non-string types: {e}")

        # Challenge 1.7: Query with duplicate difficulties
        try:
            res_dups = sm.list_pending(difficulties=["Medium", "medium", "MEDIUM", "  Medium  "])
            if len(res_dups) == expected_counts["medium"]:
                results.record_pass("Duplicate Difficulties Deduplication", f"Retrieved {len(res_dups)} tasks matching expected {expected_counts['medium']}")
            else:
                results.record_fail("Duplicate Difficulties Deduplication", f"Retrieved {len(res_dups)}, expected {expected_counts['medium']}")
        except Exception as e:
            results.record_fail("Duplicate Difficulties Deduplication", f"Exception: {e}")

        # Challenge 1.8: Query with 1,000 difficulty values (stressing SQLite query parameters)
        try:
            large_diff_list = [f"diff_{i}" for i in range(900)] + ["Medium"]
            res_large = sm.list_pending(difficulties=large_diff_list)
            if len(res_large) == expected_counts["medium"]:
                results.record_pass("900+ Parameter Difficulties List", f"Retrieved {len(res_large)} tasks without exceeding SQLite parameter limits")
            else:
                results.record_fail("900+ Parameter Difficulties List", f"Retrieved {len(res_large)}, expected {expected_counts['medium']}")
        except Exception as e:
            results.record_fail("900+ Parameter Difficulties List", f"Exception: {e}")

        # Challenge 1.9: Limit parameter enforcement
        try:
            res_limit_5 = sm.list_pending(difficulties=["Medium"], limit=5)
            if len(res_limit_5) == 5:
                results.record_pass("Limit=5 Enforcement", "Returned exactly 5 tasks")
            else:
                results.record_fail("Limit=5 Enforcement", f"Returned {len(res_limit_5)} tasks, expected 5")

            res_limit_0 = sm.list_pending(difficulties=["Medium"], limit=0)
            if len(res_limit_0) == 0:
                results.record_pass("Limit=0 Enforcement", "Returned exactly 0 tasks")
            else:
                results.record_fail("Limit=0 Enforcement", f"Returned {len(res_limit_0)} tasks, expected 0")
        except Exception as e:
            results.record_fail("Limit Enforcement", f"Exception: {e}")

        # Challenge 1.10: get_pending_tasks alias interface contract
        try:
            alias_res = sm.get_pending_tasks(platform="guvi_codekata", difficulties=["Hard"])
            direct_res = sm.list_pending(platform="guvi_codekata", difficulties=["Hard"])
            if len(alias_res) == len(direct_res) and [t.task_id for t in alias_res] == [t.task_id for t in direct_res]:
                results.record_pass("get_pending_tasks Interface Contract", f"Alias perfectly matches list_pending ({len(alias_res)} tasks)")
            else:
                results.record_fail("get_pending_tasks Interface Contract", "Mismatch between alias and list_pending")
        except Exception as e:
            results.record_fail("get_pending_tasks Interface Contract", f"Exception: {e}")

        # Challenge 1.11: Behavior when difficulties=None and DB contains corrupt metadata
        try:
            # When difficulties=None, the query fetches all tasks. Corrupt metadata rows may cause json.loads() error in _row_to_task
            res_all = sm.list_pending(difficulties=None)
            results.record_pass("list_pending(difficulties=None) with corrupt DB", f"Retrieved {len(res_all)} tasks")
        except json.decoder.JSONDecodeError as jde:
            results.record_fail("list_pending(difficulties=None) with corrupt DB", f"VULNERABILITY: json.decoder.JSONDecodeError in _row_to_task: {jde}")
        except Exception as e:
            results.record_fail("list_pending(difficulties=None) with corrupt DB", f"Exception: {e}")


def test_concurrency(results: TestResults):
    print("\n--- TEST SUITE 2: Concurrent Concurrency Test Harness ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "concurrent_state.db"
        json_path = Path(tmpdir) / "concurrent_state.json"
        sm = StateManager(db_path=str(db_path), json_export_path=str(json_path))

        # Seed 200 tasks
        for i in range(200):
            diff = ["Easy", "Medium", "Hard"][i % 3]
            sm.record_task(
                task_id=f"concurrent-{i:03d}",
                platform="guvi_codekata",
                category="Basics",
                title=f"Concurrent Task {i}",
                metadata={"difficulty": diff, "index": i},
                auto_export_json=False
            )

        errors = []
        stop_event = threading.Event()

        def reader_worker(thread_id: int):
            try:
                for iteration in range(50):
                    if stop_event.is_set():
                        break
                    diff = ["Medium", "Hard", "Easy"][iteration % 3]
                    tasks = sm.list_pending(difficulties=[diff], limit=10)
                    assert isinstance(tasks, list)
                    # Verify task metadata
                    for t in tasks:
                        assert t.metadata.get("difficulty").lower() == diff.lower()
                    time.sleep(0.001)
            except Exception as e:
                errors.append(f"Reader thread {thread_id} crashed: {e}")

        def writer_worker(thread_id: int):
            try:
                for iteration in range(30):
                    if stop_event.is_set():
                        break
                    task_id = f"concurrent-{(iteration * 5) % 200:03d}"
                    sm.update_task_status(
                        task_id=task_id,
                        status="IN_PROGRESS" if iteration % 2 == 0 else "PENDING",
                        metadata_update={"worker_ping": iteration, "thread": thread_id},
                        auto_export_json=False
                    )
                    time.sleep(0.002)
            except Exception as e:
                errors.append(f"Writer thread {thread_id} crashed: {e}")

        threads = []
        # Launch 8 reader threads
        for t_idx in range(8):
            t = threading.Thread(target=reader_worker, args=(t_idx,))
            threads.append(t)

        # Launch 4 writer threads
        for t_idx in range(4):
            t = threading.Thread(target=writer_worker, args=(t_idx,))
            threads.append(t)

        start_time = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10.0)

        elapsed = time.time() - start_time
        alive = [t for t in threads if t.is_alive()]
        if alive:
            stop_event.set()
            results.record_fail("Concurrency Deadlock", f"{len(alive)} threads timed out after 10s")
        elif errors:
            results.record_fail("Concurrent Execution Errors", "; ".join(errors))
        else:
            results.record_pass("Concurrent Concurrency (8 Readers, 4 Writers)", f"Completed in {elapsed:.2f}s with 0 errors/deadlocks")


def test_cli_parser(results: TestResults):
    print("\n--- TEST SUITE 3: CLI Parser & Difficulties Normalization Stress ---")

    # 3.1 Difficulty normalizer unit stress
    diff_test_cases = [
        # Input, Expected Output
        ("Medium, Hard", ["Medium", "Hard"]),
        ("medium,hard", ["Medium", "Hard"]),
        ("EASY", ["Easy"]),
        (["Medium,Hard"], ["Medium", "Hard"]),
        (["Medium", "Hard"], ["Medium", "Hard"]),
        (["Easy", "Medium", "Hard"], ["Easy", "Medium", "Hard"]),
        (["Medium", "medium", "MEDIUM"], ["Medium"]),  # deduplication
        ("Invalid", None),
        ("Invalid,Medium", ["Medium"]),
        ("123, Hard", ["Hard"]),
        ("", None),
        (None, None),
        (["", "  ", ",,"], None),
        ("  medium  ,  hard  ", ["Medium", "Hard"]),
        ("EASY, medium, HARD", ["Easy", "Medium", "Hard"]),
    ]

    for raw, expected in diff_test_cases:
        actual = parse_difficulties(raw)
        if actual == expected:
            results.record_pass(f"parse_difficulties({raw!r})", f"-> {actual}")
        else:
            results.record_fail(f"parse_difficulties({raw!r})", f"Expected {expected}, got {actual}")

    # 3.2 CLI Parser Flag Ordering & Defaults
    parser = create_cli_parser()

    cli_scenarios = [
        # (Args, Expected command, Expected headless, Expected limit, Description)
        (["run-codekata"], "run-codekata", True, None, "Default run-codekata headless=True"),
        (["run-zenclass"], "run-zenclass", False, None, "Default run-zenclass headless=False"),
        (["run-all"], "run-all", False, None, "Default run-all headless=False"),
        ([], None, False, None, "Root default headless=False"),
        
        # Subcommand then flag
        (["run-codekata", "--headless"], "run-codekata", True, None, "run-codekata --headless"),
        (["run-codekata", "--no-headless"], "run-codekata", False, None, "run-codekata --no-headless"),
        (["run-codekata", "--headed"], "run-codekata", False, None, "run-codekata --headed"),
        (["run-zenclass", "--headless"], "run-zenclass", True, None, "run-zenclass --headless"),
        
        # Flag before subcommand
        (["--headless", "run-zenclass"], "run-zenclass", True, None, "--headless run-zenclass"),
        (["--no-headless", "run-codekata"], "run-codekata", False, None, "--no-headless run-codekata"),
        (["--headed", "run-codekata"], "run-codekata", False, None, "--headed run-codekata"),
        
        # Limits before and after subcommand
        (["run-codekata", "--limit", "10"], "run-codekata", True, 10, "run-codekata --limit 10"),
        (["--limit", "15", "run-codekata"], "run-codekata", True, 15, "--limit 15 run-codekata"),
        (["--limit", "5", "run-codekata", "--headed"], "run-codekata", False, 5, "Mixed flags before/after"),

        # Overriding conflicting flags (last flag wins)
        (["run-codekata", "--headless", "--headed"], "run-codekata", False, None, "--headless followed by --headed"),
        (["run-codekata", "--headed", "--headless"], "run-codekata", True, None, "--headed followed by --headless"),
        (["--headless", "run-codekata", "--headed"], "run-codekata", False, None, "Root --headless overridden by subcommand --headed"),
        (["--headed", "run-codekata", "--headless"], "run-codekata", True, None, "Root --headed overridden by subcommand --headless"),
    ]

    for args, exp_cmd, exp_hl, exp_lim, desc in cli_scenarios:
        try:
            ns = parser.parse_args(args)
            if ns.command == exp_cmd and ns.headless == exp_hl and getattr(ns, "limit", None) == exp_lim:
                results.record_pass(f"CLI: {desc}", f"command={ns.command}, headless={ns.headless}, limit={getattr(ns, 'limit', None)}")
            else:
                results.record_fail(
                    f"CLI: {desc}",
                    f"Expected cmd={exp_cmd}, headless={exp_hl}, limit={exp_lim} | Got cmd={ns.command}, headless={ns.headless}, limit={getattr(ns, 'limit', None)}"
                )
        except Exception as e:
            results.record_fail(f"CLI: {desc}", f"Exception: {e}")

    # 3.3 CLI Parser Difficulty Options
    diff_cli_scenarios = [
        (["run-codekata", "--difficulty", "Medium,Hard"], ["Medium,Hard"], ["Medium", "Hard"]),
        (["run-codekata", "--difficulty", "Medium", "--difficulty", "Hard"], ["Medium", "Hard"], ["Medium", "Hard"]),
        (["run-codekata", "--difficulty", "easy"], ["easy"], ["Easy"]),
        (["run-all", "--difficulty", "Medium,Hard"], ["Medium,Hard"], ["Medium", "Hard"]),
    ]

    for args, exp_raw, exp_parsed in diff_cli_scenarios:
        try:
            ns = parser.parse_args(args)
            raw = getattr(ns, "difficulty", None)
            parsed = parse_difficulties(raw)
            if raw == exp_raw and parsed == exp_parsed:
                results.record_pass(f"CLI Difficulty: {' '.join(args)}", f"raw={raw} -> parsed={parsed}")
            else:
                results.record_fail(f"CLI Difficulty: {' '.join(args)}", f"Expected raw={exp_raw}, parsed={exp_parsed} | Got raw={raw}, parsed={parsed}")
        except Exception as e:
            results.record_fail(f"CLI Difficulty: {' '.join(args)}", f"Exception: {e}")


def test_extractor_css_sanitization(results: TestResults):
    print("\n--- TEST SUITE 4: Extractor CSS Sanitization Adversarial Stress ---")

    # Case 1: Spaced style tags and inline styles
    html_with_spaced_style = """
    <div>
        <h1>Sum of Array</h1>
        <p>Problem Description: Given an array of integers, find the sum.</p>
        <style >
            .test { display: inline-flex; font-size: 14px; }
        </ style>
        <p>Sample Input: 5 10 15</p>
        <p>Sample Output: 30</p>
    </div>
    """
    spec = ProblemExtractor.extract(html_with_spaced_style)
    if len(spec.sample_cases) == 1 and spec.sample_cases[0].input.strip() == "5 10 15" and spec.sample_cases[0].expected_output.strip() == "30":
        results.record_pass("Extractor: Spaced closing style tag", "Sample case cleanly extracted")
    else:
        results.record_fail("Extractor: Spaced closing style tag", f"Extracted {len(spec.sample_cases)} cases: {spec.sample_cases}")

    # Case 2: Pure CSS block should NOT be extracted as sample input
    html_with_css_selector = """
    <div>
        <h1>Factorial</h1>
        <p>Calculate factorial.</p>
        input {
            display: inline-flex;
            font-size: inherit;
            line-height: inherit;
            flex: 1;
        }
        <p>Sample Input: 5</p>
        <p>Sample Output: 120</p>
    </div>
    """
    spec2 = ProblemExtractor.extract(html_with_css_selector)
    if len(spec2.sample_cases) == 1 and spec2.sample_cases[0].input.strip() == "5" and spec2.sample_cases[0].expected_output.strip() == "120":
        results.record_pass("Extractor: CSS 'input {' selector rejected", "Sample cases free of CSS selector leaks")
    else:
        results.record_fail("Extractor: CSS 'input {' selector rejected", f"Extracted {len(spec2.sample_cases)} cases: {spec2.sample_cases}")

    # Case 3: Legitimate Python/JSON code containing CSS property names MUST BE PRESERVED
    html_with_json_code = """
    <div>
        <h1>JSON Parser</h1>
        <p>You are designing a web component parser. Parse the given JSON config.</p>
        <p>Sample Input: {"display": "inline-flex", "flex": 1, "font-size": 16}</p>
        <p>Sample Output: VALID</p>
    </div>
    """
    spec3 = ProblemExtractor.extract(html_with_json_code)
    if len(spec3.sample_cases) == 1 and '"display": "inline-flex"' in spec3.sample_cases[0].input:
        results.record_pass("Extractor: Legitimate JSON preservation", "JSON with CSS properties preserved intact")
    else:
        results.record_fail("Extractor: Legitimate JSON preservation", f"Corrupted JSON sample: {spec3.sample_cases}")

    # Case 4: C++ / Java code block with braces
    html_with_cpp_code = """
    <div>
        <h1>Block Output</h1>
        <p>Print the output of the block.</p>
        <p>Sample Input: { int display = 10; int flex = 20; return display + flex; }</p>
        <p>Sample Output: 30</p>
    </div>
    """
    spec4 = ProblemExtractor.extract(html_with_cpp_code)
    if len(spec4.sample_cases) == 1 and 'int display = 10' in spec4.sample_cases[0].input:
        results.record_pass("Extractor: Code block preservation", "Code block with 'display' and 'flex' preserved")
    else:
        results.record_fail("Extractor: Code block preservation", f"Corrupted code block: {spec4.sample_cases}")


def main():
    print("======================================================================")
    print("Milestone 1 Challenger Stress Test Harness - Starting Execution")
    print("======================================================================")

    results = TestResults()

    test_1000_synthetic_tasks(results)
    test_concurrency(results)
    test_cli_parser(results)
    test_extractor_css_sanitization(results)

    print("\n======================================================================")
    print(f"Summary: {results.passed} PASSED, {results.failed} FAILED")
    print("======================================================================")

    if results.failed > 0:
        print("\nFailures:")
        for name, reason in results.errors:
            print(f"- {name}: {reason}")
        sys.exit(1)
    else:
        print("\nAll stress tests PASSED successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
