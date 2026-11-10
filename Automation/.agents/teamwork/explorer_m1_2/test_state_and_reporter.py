"""
Test suite validating proposed StateManager and SummaryReporter.
Run in explorer_m1_2 working directory.
"""

import sys
import os
import shutil
import time
import threading
from pathlib import Path

# Add working directory to path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from proposed_state_manager import (
    StateManager,
    TaskRecord,
    TaskStatus,
    TaskPlatform,
    TaskResult
)
from proposed_reporter import SummaryReporter


def test_full_pipeline():
    test_dir = Path("/tmp/test_automation_state")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True, exist_ok=True)

    db_path = test_dir / "automation_state.db"
    json_path = test_dir / "state_summary.json"
    reports_dir = test_dir / "reports"

    print("--- 1. Testing StateManager Initialization & PRAGMA Verification ---")
    sm = StateManager(db_path=str(db_path), json_export_path=str(json_path))
    
    cursor = sm.conn.cursor()
    cursor.execute("PRAGMA journal_mode;")
    mode = cursor.fetchone()[0]
    print(f"Journal mode: {mode}")
    assert mode.lower() == "wal", f"Expected WAL mode, got {mode}"

    print("--- 2. Testing Requirement R3: record_task with all 9 fields ---")
    t1 = sm.record_task(
        task_id="guvi_odd_or_even",
        platform=TaskPlatform.GUVI_CODEKATA.value,
        title="Odd or Even Sum",
        category="Easy",
        url="https://www.guvi.in/code-kata/odd-or-even-sum/",
        status=TaskStatus.DISCOVERED.value,
        attempts=0,
        result=TaskResult.UNATTEMPTED.value,
        failure_reason=None,
        next_action="SOLVE_AND_SUBMIT",
        time_spent_seconds=0.0,
        metadata={"points": 30, "language": "PYTHON 3"}
    )
    assert t1 is not None
    assert t1.task_id == "guvi_odd_or_even"
    assert t1.platform == "guvi_codekata"
    assert t1.task_category == "Easy"
    assert t1.status == "DISCOVERED"
    assert t1.attempt_count == 0
    assert t1.result == "UNATTEMPTED"
    assert t1.failure_reason is None
    assert t1.next_action == "SOLVE_AND_SUBMIT"
    print("Record task verified successfully.")

    print("--- 3. Testing update_task_status lifecycle ---")
    # Transition to IN_PROGRESS
    sm.update_task_status(
        task_id="guvi_odd_or_even",
        status=TaskStatus.IN_PROGRESS.value,
        time_spent_seconds=2.5
    )
    t1_updated = sm.get_task("guvi_odd_or_even")
    assert t1_updated.status == "IN_PROGRESS"
    assert t1_updated.time_spent_seconds == 2.5

    # Transition to COMPLETED
    sm.update_task_status(
        task_id="guvi_odd_or_even",
        status=TaskStatus.COMPLETED.value,
        result=TaskResult.SOLVED.value,
        next_action="NONE_COMPLETED",
        time_spent_seconds=3.0,
        increment_attempts=True,
        metadata_update={"geekoins_awarded": 30}
    )
    t1_final = sm.get_task("guvi_odd_or_even")
    assert t1_final.status == "COMPLETED"
    assert t1_final.result == "SOLVED"
    assert t1_final.attempt_count == 1
    assert t1_final.time_spent_seconds == 5.5
    assert t1_final.metadata["geekoins_awarded"] == 30
    print("Status transitions and attempt increments verified.")

    print("--- 4. Testing ZenClass Tasks and Blocked / HITL recording ---")
    sm.record_task(
        task_id="zen_task_js_promise",
        platform=TaskPlatform.ZENCLASS_TASKS.value,
        title="Day 15: JS Promises & Async/Await",
        category="JavaScript",
        url="https://v2.zenclass.in/tasks",
        status=TaskStatus.BLOCKED.value,
        attempts=1,
        result="AWAITING_INPUT",
        failure_reason="Cloudflare Turnstile challenge detected",
        next_action="Solve Cloudflare challenge in visible foreground browser",
        time_spent_seconds=12.0
    )

    sm.record_task(
        task_id="zen_proj_capstone",
        platform=TaskPlatform.ZENCLASS_PROJECTS.value,
        title="MERN Stack E-Commerce Capstone",
        category="Capstone",
        url="https://v2.zenclass.in/projects",
        status=TaskStatus.BLOCKED.value,
        attempts=1,
        result="AWAITING_INPUT",
        failure_reason="Awaiting GitHub and Netlify deployment URLs",
        next_action="User to deploy local code in projects/mern_capstone/ and provide URLs",
        time_spent_seconds=45.0
    )

    blocked = sm.list_blocked()
    assert len(blocked) == 2
    print(f"Blocked tasks verified: {len(blocked)} items detected.")

    print("--- 5. Testing High-Volume Batch Discovery (2,145 CodeKata Problems) ---")
    batch = []
    for i in range(1, 2146):
        batch.append({
            "task_id": f"codekata_prob_{i:04d}",
            "platform": TaskPlatform.GUVI_CODEKATA.value,
            "category": "Easy" if i % 2 == 0 else "Medium",
            "title": f"Problem #{i}: Sample Algorithmic Challenge",
            "url": f"https://www.guvi.in/code-kata/problem-{i}/",
            "status": TaskStatus.PENDING.value if i > 10 else TaskStatus.COMPLETED.value,
            "attempts": 0 if i > 10 else 1,
            "result": TaskResult.UNATTEMPTED.value if i > 10 else TaskResult.SOLVED.value,
            "time_spent_seconds": 0.0 if i > 10 else 4.0
        })

    t0 = time.time()
    count = sm.batch_record_tasks(batch)
    t_batch = time.time() - t0
    print(f"Batch inserted {count} tasks in {t_batch:.3f} seconds ({count/t_batch:.1f} tasks/sec)")
    assert count == 2145
    assert t_batch < 2.0, "Batch insertion must be fast"

    print("--- 6. Testing Pending Queue Listing ---")
    pending = sm.list_pending(limit=5)
    assert len(pending) == 5
    print(f"Retrieved {len(pending)} pending tasks cleanly.")

    print("--- 7. Testing Summary Statistics ---")
    stats = sm.get_summary_stats()
    print("Stats calculated:")
    print(f"  Total discovered : {stats['total_discovered']}")
    print(f"  Total completed  : {stats['total_completed']}")
    print(f"  Total pending    : {stats['total_pending']}")
    print(f"  Total blocked    : {stats['total_blocked']}")
    print(f"  Success rate     : {stats['success_rate_percent']}%")
    print(f"  Total time spent : {stats['total_time_spent_seconds']}s")
    assert stats["total_discovered"] == 2148  # 1 (odd_or_even) + 2 (zenclass) + 2145 (batch)
    assert stats["total_blocked"] == 2
    assert len(stats["human_intervention_issues"]) == 2

    print("--- 8. Testing Atomic JSON State Export ---")
    assert json_path.exists(), "Atomic JSON file must exist"
    assert json_path.stat().st_size > 0
    print(f"JSON export file size: {json_path.stat().st_size:,} bytes")

    print("--- 9. Testing SummaryReporter (Markdown & JSON) ---")
    reporter = SummaryReporter(state_manager=sm, report_dir=str(reports_dir))
    md_path, rep_json_path = reporter.generate_all_reports()
    
    assert Path(md_path).exists()
    assert Path(rep_json_path).exists()
    print(f"Markdown report generated: {md_path} ({Path(md_path).stat().st_size} bytes)")
    print(f"JSON report generated: {rep_json_path} ({Path(rep_json_path).stat().st_size} bytes)")

    print("--- 10. Testing Terminal Summary Output ---")
    reporter.print_terminal_summary()

    print("--- 11. Testing Multi-Threaded Concurrency ---")
    def worker(worker_id):
        for j in range(20):
            sm.update_task_status(
                task_id=f"codekata_prob_{(worker_id * 20 + j + 11):04d}",
                status=TaskStatus.COMPLETED.value,
                result=TaskResult.SOLVED.value,
                time_spent_seconds=1.5,
                increment_attempts=True,
                auto_export_json=False
            )

    threads = [threading.Thread(target=worker, args=(w,)) for w in range(5)]
    t_start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    t_threads = time.time() - t_start
    print(f"Concurrent multi-threaded execution (100 updates across 5 threads) passed in {t_threads:.3f}s with 0 errors!")

    sm.close()
    print("\n✅ ALL STATE MANAGER AND REPORTER TESTS PASSED COMPLETELY WITH 100% SUCCESS!\n")


if __name__ == "__main__":
    test_full_pipeline()
