#!/usr/bin/env python3
"""
stress_harness.py - Empirical Adversarial Stress Harness for Milestone 1
Tests:
  1. Multi-Threaded Concurrency (10 to 50 threads) on StateManager
  2. Concurrent Atomic JSON Export & High-Frequency Reader Collision
  3. Crash Recovery, WAL Checkpointing & Process Reconnection
  4. Multi-Process Concurrency (Subprocesses)
  5. Edge Cases (SQL Injection, Unicode, Huge Payloads, Batch Boundaries)
  6. CLI Execution & Validation
"""

import os
import sys
import time
import json
import uuid
import sqlite3
import shutil
import tempfile
import threading
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List

# Ensure zenclass_guvi is in sys.path
PROJECT_ROOT = Path("/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi").resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.state_manager import StateManager, TaskRecord, TaskStatus, TaskResult
from core.reporter import SummaryReporter


class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.errors: List[str] = []
        self.metrics: Dict[str, Any] = {}
        self.duration_seconds = 0.0

    def record_pass(self, **metrics):
        self.passed = True
        self.metrics.update(metrics)

    def record_fail(self, error: str, **metrics):
        self.passed = False
        self.errors.append(error)
        self.metrics.update(metrics)


# =============================================================================
# 1. Multi-Threaded Concurrency
# =============================================================================

def test_1a_concurrency_10_threads(temp_dir: str) -> TestResult:
    res = TestResult("1A: Concurrency 10 Threads (50 tasks/thread = 500 tasks)")
    t0 = time.perf_counter()
    db_file = os.path.join(temp_dir, "test_1a.db")
    json_file = os.path.join(temp_dir, "test_1a.json")
    sm = StateManager(db_path=db_file, json_export_path=json_file)

    num_threads = 10
    tasks_per_thread = 50
    total_expected = num_threads * tasks_per_thread
    exceptions: List[Exception] = []

    def worker(thread_idx: int):
        for i in range(tasks_per_thread):
            try:
                task_id = f"t1a_th{thread_idx}_task{i:03d}"
                sm.record_task(
                    task_id=task_id,
                    platform="guvi_codekata" if i % 2 == 0 else "zenclass_tasks",
                    title=f"Task {thread_idx}-{i}",
                    category="Algorithms" if i % 2 == 0 else "Frontend",
                    url=f"https://example.com/task/{task_id}",
                    status="completed" if i % 3 == 0 else "pending",
                    attempts=1 if i % 3 == 0 else 0,
                    result="SOLVED" if i % 3 == 0 else "UNATTEMPTED",
                    failure_reason=None,
                    next_action="NONE" if i % 3 == 0 else "SOLVE",
                    time_spent_seconds=float(i * 1.5),
                    metadata={"thread": thread_idx, "iter": i},
                    auto_export_json=True
                )
            except Exception as e:
                exceptions.append(e)

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    res.duration_seconds = time.perf_counter() - t0

    if exceptions:
        res.record_fail(f"Exceptions caught in worker threads: {len(exceptions)}: {exceptions[0]}",
                        exceptions_count=len(exceptions))
        sm.close()
        return res

    # Verify data integrity
    all_tasks = sm.list_tasks()
    if len(all_tasks) != total_expected:
        res.record_fail(f"Row count mismatch: expected {total_expected}, got {len(all_tasks)}")
        sm.close()
        return res

    stats = sm.get_summary_stats()
    if stats["total_discovered"] != total_expected:
        res.record_fail(f"Summary stats mismatch: expected {total_expected}, got {stats['total_discovered']}")
        sm.close()
        return res

    sm.close()
    res.record_pass(
        total_tasks=total_expected,
        throughput_tasks_per_sec=round(total_expected / res.duration_seconds, 2),
        duration_s=round(res.duration_seconds, 3)
    )
    return res


def test_1b_concurrency_50_threads(temp_dir: str) -> TestResult:
    res = TestResult("1B: Concurrency 50 Threads (20 tasks/thread = 1,000 tasks)")
    t0 = time.perf_counter()
    db_file = os.path.join(temp_dir, "test_1b.db")
    json_file = os.path.join(temp_dir, "test_1b.json")
    sm = StateManager(db_path=db_file, json_export_path=json_file)

    num_threads = 50
    tasks_per_thread = 20
    total_expected = num_threads * tasks_per_thread
    exceptions: List[Exception] = []

    def worker(thread_idx: int):
        for i in range(tasks_per_thread):
            try:
                task_id = f"t1b_th{thread_idx}_task{i:03d}"
                sm.record_task(
                    task_id=task_id,
                    platform="guvi_codekata" if thread_idx % 2 == 0 else "zenclass_projects",
                    title=f"Stress Task {thread_idx}-{i}",
                    category="System",
                    status="in_progress" if i % 2 == 0 else "pending",
                    attempts=1,
                    auto_export_json=False  # Focus on pure DB write throughput
                )
            except Exception as e:
                exceptions.append(e)

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    res.duration_seconds = time.perf_counter() - t0

    if exceptions:
        res.record_fail(f"Exceptions caught: {len(exceptions)}: {exceptions[0]}",
                        exceptions_count=len(exceptions))
        sm.close()
        return res

    all_tasks = sm.list_tasks()
    if len(all_tasks) != total_expected:
        res.record_fail(f"Row count mismatch: expected {total_expected}, got {len(all_tasks)}")
        sm.close()
        return res

    sm.close()
    res.record_pass(
        total_tasks=total_expected,
        threads=num_threads,
        throughput_tasks_per_sec=round(total_expected / res.duration_seconds, 2),
        duration_s=round(res.duration_seconds, 3)
    )
    return res


def test_1c_mixed_concurrency_workload(temp_dir: str) -> TestResult:
    res = TestResult("1C: Mixed Concurrency (Writes, Status Updates, Reads, Stats)")
    t0 = time.perf_counter()
    db_file = os.path.join(temp_dir, "test_1c.db")
    sm = StateManager(db_path=db_file)

    # Pre-populate 200 tasks
    pre_tasks = [
        {"task_id": f"seed_{i}", "platform": "guvi", "title": f"Seed {i}", "status": "pending"}
        for i in range(200)
    ]
    sm.batch_record_tasks(pre_tasks, auto_export_json=False)

    exceptions: List[Exception] = []
    stop_signal = threading.Event()

    def writer_worker(idx: int):
        for i in range(30):
            if stop_signal.is_set():
                break
            try:
                sm.record_task(
                    task_id=f"new_{idx}_{i}",
                    platform="zenclass_tasks",
                    title=f"New Task {idx}-{i}",
                    status="pending",
                    auto_export_json=False
                )
            except Exception as e:
                exceptions.append(e)

    def updater_worker():
        for i in range(50):
            if stop_signal.is_set():
                break
            try:
                target_id = f"seed_{i % 200}"
                sm.update_task_status(
                    task_id=target_id,
                    status="completed",
                    result="SOLVED",
                    increment_attempts=True,
                    auto_export_json=False
                )
            except Exception as e:
                exceptions.append(e)

    def reader_worker():
        while not stop_signal.is_set():
            try:
                _ = sm.list_pending()
                _ = sm.get_summary_stats()
                time.sleep(0.005)
            except Exception as e:
                exceptions.append(e)

    threads = []
    # 15 writers
    for i in range(15):
        threads.append(threading.Thread(target=writer_worker, args=(i,)))
    # 10 updaters
    for _ in range(10):
        threads.append(threading.Thread(target=updater_worker))
    # 10 readers
    for _ in range(10):
        threads.append(threading.Thread(target=reader_worker))

    for t in threads:
        t.start()

    # Wait for writers and updaters
    for t in threads[:25]:
        t.join()

    stop_signal.set()
    for t in threads[25:]:
        t.join()

    res.duration_seconds = time.perf_counter() - t0

    if exceptions:
        res.record_fail(f"Exceptions during mixed workload: {len(exceptions)}: {exceptions[0]}")
        sm.close()
        return res

    # Verify DB consistency
    stats = sm.get_summary_stats()
    expected_discovered = 200 + (15 * 30)
    if stats["total_discovered"] != expected_discovered:
        res.record_fail(f"Discovered count mismatch: expected {expected_discovered}, got {stats['total_discovered']}")
        sm.close()
        return res

    sm.close()
    res.record_pass(
        total_discovered=stats["total_discovered"],
        total_completed=stats["total_completed"],
        duration_s=round(res.duration_seconds, 3)
    )
    return res


# =============================================================================
# 2. Atomic JSON Export Integrity
# =============================================================================

def test_2a_concurrent_export_and_reader(temp_dir: str) -> TestResult:
    res = TestResult("2A: Atomic JSON Export Collision (Writers vs Concurrent Readers)")
    t0 = time.perf_counter()
    db_file = os.path.join(temp_dir, "test_2a.db")
    json_file = os.path.join(temp_dir, "state_summary_2a.json")
    sm = StateManager(db_path=db_file, json_export_path=json_file)

    # Seed initial 50 tasks
    sm.batch_record_tasks([
        {"task_id": f"init_{i}", "platform": "guvi", "title": f"Initial {i}", "status": "completed"}
        for i in range(50)
    ])
    sm.export_state_json(json_file)

    stop_event = threading.Event()
    read_counts = [0]
    decode_errors: List[str] = []
    empty_file_errors: List[str] = []
    write_exceptions: List[str] = []

    def writer_loop():
        counter = 0
        while not stop_event.is_set():
            try:
                task_id = f"writer_task_{counter}"
                sm.record_task(
                    task_id=task_id,
                    platform="guvi",
                    title=f"Writer Task {counter}",
                    status="completed" if counter % 2 == 0 else "pending",
                    auto_export_json=True
                )
                counter += 1
            except Exception as e:
                write_exceptions.append(str(e))
            time.sleep(0.002)

    def reader_loop():
        local_reads = 0
        while not stop_event.is_set():
            if not os.path.exists(json_file):
                time.sleep(0.001)
                continue
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if not content.strip():
                        empty_file_errors.append("File read was empty!")
                    else:
                        data = json.loads(content)
                        assert "summary" in data
                        assert "tasks" in data
                        local_reads += 1
            except json.JSONDecodeError as jde:
                decode_errors.append(f"JSONDecodeError: {jde} on content snippet: {content[:100]}")
            except Exception as e:
                decode_errors.append(f"Unexpected reader error: {e}")
            time.sleep(0.001)
        read_counts[0] += local_reads

    # Start 4 writers and 8 readers
    threads = []
    for _ in range(4):
        threads.append(threading.Thread(target=writer_loop))
    for _ in range(8):
        threads.append(threading.Thread(target=reader_loop))

    for t in threads:
        t.start()

    time.sleep(3.0)  # Run collision test for 3 seconds
    stop_event.set()

    for t in threads:
        t.join()

    res.duration_seconds = time.perf_counter() - t0
    sm.close()

    if decode_errors:
        res.record_fail(f"JSONDecodeErrors encountered during atomic export: {len(decode_errors)}: {decode_errors[0]}")
        return res
    if empty_file_errors:
        res.record_fail(f"Empty file reads encountered: {len(empty_file_errors)}")
        return res
    if write_exceptions:
        res.record_fail(f"Write exceptions during concurrent export: {len(write_exceptions)}: {write_exceptions[0]}")
        return res

    res.record_pass(
        total_atomic_reads=read_counts[0],
        read_ops_per_sec=round(read_counts[0] / res.duration_seconds, 1),
        decode_errors_count=0,
        empty_reads_count=0
    )
    return res


# =============================================================================
# 3. Database Recovery & Reconnection
# =============================================================================

def test_3a_wal_recovery_after_abrupt_close(temp_dir: str) -> TestResult:
    res = TestResult("3A: WAL Recovery After Abrupt Close")
    t0 = time.perf_counter()
    db_file = os.path.join(temp_dir, "test_3a.db")

    # Step 1: Open SM, insert 300 tasks, verify WAL file exists
    sm1 = StateManager(db_path=db_file)
    for i in range(300):
        sm1.record_task(
            task_id=f"recov_{i:04d}",
            platform="guvi",
            title=f"Recovery Task {i}",
            status="completed" if i % 2 == 0 else "pending",
            auto_export_json=False
        )

    # Abruptly close the connection without checkpointing
    sm1.conn.close()

    # Verify database file exists
    if not os.path.exists(db_file):
        res.record_fail("Database file missing after close")
        return res

    # Step 2: Open fresh StateManager instance on the same file
    sm2 = StateManager(db_path=db_file)
    all_tasks = sm2.list_tasks()
    if len(all_tasks) != 300:
        res.record_fail(f"Recovery failed: expected 300 tasks, got {len(all_tasks)}")
        sm2.close()
        return res

    # Run PRAGMA integrity_check
    cursor = sm2.conn.cursor()
    cursor.execute("PRAGMA integrity_check;")
    rows = cursor.fetchall()
    integrity_status = rows[0][0] if rows else "UNKNOWN"

    if integrity_status != "ok":
        res.record_fail(f"PRAGMA integrity_check returned '{integrity_status}' instead of 'ok'")
        sm2.close()
        return res

    stats = sm2.get_summary_stats()
    if stats["total_discovered"] != 300 or stats["total_completed"] != 150:
        res.record_fail(f"Summary stats inaccurate after recovery: {stats}")
        sm2.close()
        return res

    sm2.close()
    res.duration_seconds = time.perf_counter() - t0
    res.record_pass(
        recovered_tasks=300,
        integrity_check=integrity_status,
        duration_s=round(res.duration_seconds, 3)
    )
    return res


def test_3b_multiprocess_wal_concurrency(temp_dir: str) -> TestResult:
    res = TestResult("3B: Multi-Process WAL Concurrency (Subprocesses)")
    t0 = time.perf_counter()
    db_file = os.path.join(temp_dir, "test_3b.db")

    # Initialize DB schema
    sm_init = StateManager(db_path=db_file)
    sm_init.close()

    # Worker script code to run in independent subprocesses
    worker_script = f"""
import sys
sys.path.insert(0, '{str(PROJECT_ROOT)}')
from core.state_manager import StateManager

process_id = int(sys.argv[1])
db_path = '{db_file}'
sm = StateManager(db_path=db_path)

for i in range(50):
    sm.record_task(
        task_id=f"proc_{{process_id}}_{{i}}",
        platform="guvi",
        title=f"Process {{process_id}} Task {{i}}",
        status="pending",
        auto_export_json=False
    )
sm.close()
"""
    script_path = os.path.join(temp_dir, "proc_worker.py")
    with open(script_path, "w") as f:
        f.write(worker_script)

    # Spawn 6 separate Python processes
    num_procs = 6
    procs = []
    for pid in range(num_procs):
        p = subprocess.Popen(
            [sys.executable, script_path, str(pid)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        procs.append(p)

    errors = []
    for pid, p in enumerate(procs):
        out, err = p.communicate(timeout=20)
        if p.returncode != 0:
            errors.append(f"Process {pid} exited with code {p.returncode}: {err.decode('utf-8')}")

    res.duration_seconds = time.perf_counter() - t0

    if errors:
        res.record_fail(f"Subprocess concurrency errors: {errors}")
        return res

    # Verify all records from all processes
    sm_verify = StateManager(db_path=db_file)
    all_tasks = sm_verify.list_tasks()
    expected = num_procs * 50
    if len(all_tasks) != expected:
        res.record_fail(f"Multi-process record count mismatch: expected {expected}, got {len(all_tasks)}")
        sm_verify.close()
        return res

    sm_verify.close()
    res.record_pass(
        num_subprocesses=num_procs,
        total_records_written=expected,
        duration_s=round(res.duration_seconds, 3)
    )
    return res


# =============================================================================
# 4. CLI Validation & Exit Codes
# =============================================================================

def test_4a_cli_no_args() -> TestResult:
    res = TestResult("4A: CLI No Arguments Exit Code")
    t0 = time.perf_counter()
    cmd = [sys.executable, str(PROJECT_ROOT / "main.py")]
    p = subprocess.run(cmd, capture_output=True, text=True)
    res.duration_seconds = time.perf_counter() - t0

    # In main.py: if not self.args.command: return 1
    if p.returncode != 1:
        res.record_fail(f"Expected returncode 1, got {p.returncode}. stderr: {p.stderr}")
        return res

    if "No command specified" not in p.stdout and "No command specified" not in p.stderr:
        res.record_fail(f"Missing user-friendly error message. stdout: {p.stdout}")
        return res

    if "Traceback" in p.stderr:
        res.record_fail(f"Unhandled traceback found in stderr: {p.stderr}")
        return res

    res.record_pass(returncode=p.returncode, output_msg=p.stdout.strip())
    return res


def test_4b_cli_invalid_command() -> TestResult:
    res = TestResult("4B: CLI Invalid Subcommand Handling")
    t0 = time.perf_counter()
    cmd = [sys.executable, str(PROJECT_ROOT / "main.py"), "nonexistent-command-xyz"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    res.duration_seconds = time.perf_counter() - t0

    # argparse exits with code 2 on invalid choice
    if p.returncode != 2:
        res.record_fail(f"Expected returncode 2 for invalid subcommand, got {p.returncode}")
        return res

    if "Traceback" in p.stderr:
        res.record_fail(f"Unhandled traceback found in stderr: {p.stderr}")
        return res

    if "invalid choice" not in p.stderr.lower():
        res.record_fail(f"Expected argparse invalid choice message in stderr: {p.stderr}")
        return res

    res.record_pass(returncode=p.returncode)
    return res


def test_4c_cli_report_generation(temp_dir: str) -> TestResult:
    res = TestResult("4C: CLI 'report' Subcommand & Artifact Validation")
    t0 = time.perf_counter()
    db_file = os.path.join(temp_dir, "test_4c.db")
    reports_dir = os.path.join(temp_dir, "cli_reports")

    # Pre-populate DB with known items
    sm = StateManager(db_path=db_file)
    sm.record_task("task_01", "guvi_codekata", "Problem 1", status="completed", result="SOLVED", auto_export_json=False)
    sm.record_task("task_02", "zenclass_tasks", "Task 2", status="blocked", failure_reason="CAPTCHA encountered", auto_export_json=False)
    sm.record_task("task_03", "zenclass_projects", "Project 3", status="pending", auto_export_json=False)
    sm.close()

    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "main.py"),
        "--db-path", db_file,
        "--reports-dir", reports_dir,
        "report"
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    res.duration_seconds = time.perf_counter() - t0

    if p.returncode != 0:
        res.record_fail(f"CLI 'report' failed with code {p.returncode}. stderr: {p.stderr}")
        return res

    if "Traceback" in p.stderr:
        res.record_fail(f"Unhandled traceback in stderr: {p.stderr}")
        return res

    md_report = os.path.join(reports_dir, "SUMMARY_REPORT.md")
    json_report = os.path.join(reports_dir, "summary.json")

    if not os.path.exists(md_report):
        res.record_fail(f"Expected Markdown report at {md_report} not found")
        return res

    if not os.path.exists(json_report):
        res.record_fail(f"Expected JSON report at {json_report} not found")
        return res

    # Validate Markdown content
    with open(md_report, "r", encoding="utf-8") as f:
        md_text = f.read()

    assert "Total Tasks Discovered" in md_text
    assert "CAPTCHA encountered" in md_text
    assert "Problem 1" in md_text

    # Validate JSON structure
    with open(json_report, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    metrics = json_data.get("summary_metrics", {})
    if metrics.get("total_discovered") != 3:
        res.record_fail(f"JSON metrics total_discovered expected 3, got {metrics.get('total_discovered')}")
        return res
    if metrics.get("total_blocked") != 1:
        res.record_fail(f"JSON metrics total_blocked expected 1, got {metrics.get('total_blocked')}")
        return res

    res.record_pass(
        returncode=0,
        md_file_bytes=os.path.getsize(md_report),
        json_file_bytes=os.path.getsize(json_report)
    )
    return res


# =============================================================================
# 5. Boundary & Adversarial Injection Testing
# =============================================================================

def test_5a_adversarial_inputs_and_sql_injection(temp_dir: str) -> TestResult:
    res = TestResult("5A: Adversarial Inputs, SQL Injection & Unicode Stress")
    t0 = time.perf_counter()
    db_file = os.path.join(temp_dir, "test_5a.db")
    sm = StateManager(db_path=db_file)

    adversarial_cases = [
        ("'; DROP TABLE tasks; --", "Classic SQL Injection in task_id"),
        ("🚀🔥💻_emoji_unicode_測試_العربية", "Multi-byte Unicode, Asian and Arabic characters"),
        ("A" * 10000, "10,000 character length task_id"),
        ("<script>alert('xss')</script>", "HTML/XSS string in title"),
        ("null", "String 'null'"),
        ("{\"nested\": {\"array\": [1, 2, 3], \"bool\": true}}", "JSON string as title"),
        ("Line1\nLine2\r\nLine3\tTab", "Whitespace and newlines")
    ]

    try:
        for idx, (adv_str, desc) in enumerate(adversarial_cases):
            sm.record_task(
                task_id=f"adv_{idx}_{adv_str[:20]}",
                platform="guvi",
                title=f"Title: {adv_str}",
                category="Testing",
                failure_reason=f"Failure: {adv_str}",
                next_action=f"Action: {adv_str}",
                auto_export_json=False
            )

        # Ensure table was NOT dropped by SQL injection
        cursor = sm.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks;")
        count = cursor.fetchone()[0]
        if count != len(adversarial_cases):
            res.record_fail(f"Expected {len(adversarial_cases)} tasks, found {count}")
            sm.close()
            return res

        # Verify retrieval preserves exact strings without corruption
        for idx, (adv_str, _) in enumerate(adversarial_cases):
            t_id = f"adv_{idx}_{adv_str[:20]}"
            t = sm.get_task(t_id)
            if not t:
                res.record_fail(f"Failed to retrieve adversarial task {t_id}")
                sm.close()
                return res
            if t.title != f"Title: {adv_str}":
                res.record_fail(f"Title corrupted for {t_id}")
                sm.close()
                return res

    except Exception as e:
        res.record_fail(f"Exception during adversarial input testing: {e}")
        sm.close()
        return res

    sm.close()
    res.duration_seconds = time.perf_counter() - t0
    res.record_pass(cases_tested=len(adversarial_cases), duration_s=round(res.duration_seconds, 3))
    return res


def test_5b_batch_boundary_cases(temp_dir: str) -> TestResult:
    res = TestResult("5B: Batch Boundaries (Empty List, Duplicate IDs, 3,000 Tasks)")
    t0 = time.perf_counter()
    db_file = os.path.join(temp_dir, "test_5b.db")
    sm = StateManager(db_path=db_file)

    try:
        # 1. Empty batch
        count = sm.batch_record_tasks([], auto_export_json=False)
        if count != 0:
            res.record_fail(f"Expected 0 for empty batch, got {count}")
            sm.close()
            return res

        # 2. Duplicate IDs within same batch (ON CONFLICT should upsert cleanly)
        dup_batch = [
            {"task_id": "dup_1", "platform": "guvi", "title": "Original Title", "status": "pending"},
            {"task_id": "dup_1", "platform": "guvi", "title": "Updated Title", "status": "completed"}
        ]
        sm.batch_record_tasks(dup_batch, auto_export_json=False)
        t = sm.get_task("dup_1")
        if not t or t.status != "completed" or t.title != "Updated Title":
            res.record_fail(f"Upsert resolution failed for duplicate batch: {t}")
            sm.close()
            return res

        # 3. Large batch of 3,000 tasks (simulating full CodeKata discovery)
        large_batch = [
            {
                "task_id": f"large_{i}",
                "platform": "guvi_codekata",
                "title": f"CodeKata Problem {i}",
                "category": f"Cat_{i % 10}",
                "status": "pending"
            }
            for i in range(3000)
        ]
        t_batch_start = time.perf_counter()
        batch_res = sm.batch_record_tasks(large_batch, auto_export_json=False)
        batch_duration = time.perf_counter() - t_batch_start

        if batch_res != 3000:
            res.record_fail(f"Large batch count mismatch: expected 3000, got {batch_res}")
            sm.close()
            return res

        stats = sm.get_summary_stats()
        # 3000 + 1 (dup_1) = 3001
        if stats["total_discovered"] != 3001:
            res.record_fail(f"Discovered count mismatch: expected 3001, got {stats['total_discovered']}")
            sm.close()
            return res

    except Exception as e:
        res.record_fail(f"Exception during batch testing: {e}")
        sm.close()
        return res

    sm.close()
    res.duration_seconds = time.perf_counter() - t0
    res.record_pass(
        large_batch_size=3000,
        large_batch_duration_s=round(batch_duration, 4),
        rate_tasks_per_sec=round(3000 / batch_duration, 1)
    )
    return res


# =============================================================================
# Main Test Suite Runner
# =============================================================================

def run_all_stress_tests() -> List[TestResult]:
    temp_dir = tempfile.mkdtemp(prefix="challenger_stress_")
    print(f"[*] Initialized temporary test directory: {temp_dir}")
    results = []

    tests = [
        ("1A", lambda: test_1a_concurrency_10_threads(temp_dir)),
        ("1B", lambda: test_1b_concurrency_50_threads(temp_dir)),
        ("1C", lambda: test_1c_mixed_concurrency_workload(temp_dir)),
        ("2A", lambda: test_2a_concurrent_export_and_reader(temp_dir)),
        ("3A", lambda: test_3a_wal_recovery_after_abrupt_close(temp_dir)),
        ("3B", lambda: test_3b_multiprocess_wal_concurrency(temp_dir)),
        ("4A", test_4a_cli_no_args),
        ("4B", test_4b_cli_invalid_command),
        ("4C", lambda: test_4c_cli_report_generation(temp_dir)),
        ("5A", lambda: test_5a_adversarial_inputs_and_sql_injection(temp_dir)),
        ("5B", lambda: test_5b_batch_boundary_cases(temp_dir)),
    ]

    try:
        for code, test_fn in tests:
            print(f" -> Executing {code}...", end="", flush=True)
            res = test_fn()
            results.append(res)
            if res.passed:
                print(f" [PASS] ({res.duration_seconds:.3f}s) Metrics: {res.metrics}")
            else:
                print(f" [FAIL] ({res.duration_seconds:.3f}s) Errors: {res.errors}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"[*] Cleaned up temporary test directory: {temp_dir}")

    return results


if __name__ == "__main__":
    results = run_all_stress_tests()
    all_passed = all(r.passed for r in results)
    print("\n" + "=" * 70)
    print(f"STRESS TEST SUMMARY: {'ALL PASSED' if all_passed else 'FAILURES DETECTED'}")
    print(f"Passed: {sum(1 for r in results if r.passed)} / {len(results)}")
    print("=" * 70)
    sys.exit(0 if all_passed else 1)
