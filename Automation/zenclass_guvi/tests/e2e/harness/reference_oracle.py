"""
Authoritative Reference Oracle and Specification Ground Truth.
Provides mathematical properties, documented specifications, and interface contracts.
"""

import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
from typing import Dict, List, Optional, Any, NamedTuple


class ProblemSpec(NamedTuple):
    title: str
    description: str
    input_desc: str
    output_desc: str
    sample_input: str
    sample_output: str


class ValidationResult(NamedTuple):
    passed: bool
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: float
    error_message: Optional[str] = None


class TaskRecord(NamedTuple):
    task_id: str
    platform: str
    title: str
    category: str
    url: str
    status: str
    attempts: int
    result: str
    failure_reason: str
    next_action: str
    metadata: Optional[Dict[str, Any]] = None


# Canonical Algorithmic Problems with Ground Truth Test Vectors
CANONICAL_PROBLEMS = {
    "odd-or-even-sum": {
        "title": "Odd or Even Sum",
        "description": "Given two numbers N and M, add them and state whether the sum is even or odd.",
        "input_desc": "Two integers N and M separated by space.",
        "output_desc": "Print 'even' or 'odd' without quotes.",
        "test_vectors": [
            {"input": "9 2", "expected": "odd"},
            {"input": "10 20", "expected": "even"},
            {"input": "0 0", "expected": "even"},
            {"input": "-5 5", "expected": "even"},
            {"input": "-3 4", "expected": "odd"},
            {"input": "1000000000 1000000001", "expected": "odd"},
        ],
        "canonical_solution": (
            "import sys\n"
            "def solve():\n"
            "    line = sys.stdin.read().strip()\n"
            "    if not line: return\n"
            "    parts = line.split()\n"
            "    n, m = int(parts[0]), int(parts[1])\n"
            "    s = n + m\n"
            "    print('even' if s % 2 == 0 else 'odd')\n"
            "solve()\n"
        )
    },
    "reverse-a-string": {
        "title": "Reverse a String",
        "description": "Given a string S, print its reverse.",
        "input_desc": "A single line containing string S.",
        "output_desc": "Reversed string.",
        "test_vectors": [
            {"input": "hello", "expected": "olleh"},
            {"input": "guvi", "expected": "ivug"},
            {"input": "a", "expected": "a"},
            {"input": "12345", "expected": "54321"},
            {"input": "racecar", "expected": "racecar"},
            {"input": "Hello World!", "expected": "!dlroW olleH"},
        ],
        "canonical_solution": (
            "import sys\n"
            "def solve():\n"
            "    data = sys.stdin.read()\n"
            "    if not data: return\n"
            "    print(data.rstrip('\\r\\n')[::-1])\n"
            "solve()\n"
        )
    },
    "sum-of-array": {
        "title": "Sum of Array Elements",
        "description": "Given N elements, compute their total sum.",
        "input_desc": "First line: N. Second line: N space-separated integers.",
        "output_desc": "Total sum as a single integer.",
        "test_vectors": [
            {"input": "5\n1 2 3 4 5", "expected": "15"},
            {"input": "3\n10 -10 0", "expected": "0"},
            {"input": "1\n42", "expected": "42"},
            {"input": "4\n-1 -2 -3 -4", "expected": "-10"},
        ],
        "canonical_solution": (
            "import sys\n"
            "def solve():\n"
            "    data = sys.stdin.read().split()\n"
            "    if len(data) < 2: return\n"
            "    n = int(data[0])\n"
            "    nums = [int(x) for x in data[1:1+n]]\n"
            "    print(sum(nums))\n"
            "solve()\n"
        )
    },
    "palindrome-check": {
        "title": "Palindrome Checker",
        "description": "Determine if the given string is a palindrome.",
        "input_desc": "Single string S.",
        "output_desc": "Print 'yes' if palindrome, 'no' otherwise.",
        "test_vectors": [
            {"input": "racecar", "expected": "yes"},
            {"input": "madam", "expected": "yes"},
            {"input": "automation", "expected": "no"},
            {"input": "a", "expected": "yes"},
        ],
        "canonical_solution": (
            "import sys\n"
            "def solve():\n"
            "    s = sys.stdin.read().strip()\n"
            "    if not s: return\n"
            "    print('yes' if s == s[::-1] else 'no')\n"
            "solve()\n"
        )
    }
}


class ReferenceStateManager:
    """Canonical SQLite state manager implementing PROJECT.md contract."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    url TEXT,
                    status TEXT NOT NULL,
                    attempts INTEGER DEFAULT 0,
                    result TEXT,
                    failure_reason TEXT,
                    next_action TEXT,
                    metadata_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def record_task(
        self,
        task_id: str,
        platform: str,
        title: str,
        category: str,
        url: str,
        status: str,
        attempts: int,
        result: str,
        failure_reason: str,
        next_action: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        metadata_str = json.dumps(metadata or {})
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO tasks (
                    task_id, platform, title, category, url, status, attempts,
                    result, failure_reason, next_action, metadata_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(task_id) DO UPDATE SET
                    platform=excluded.platform,
                    title=excluded.title,
                    category=excluded.category,
                    url=excluded.url,
                    status=excluded.status,
                    attempts=excluded.attempts,
                    result=excluded.result,
                    failure_reason=excluded.failure_reason,
                    next_action=excluded.next_action,
                    metadata_json=excluded.metadata_json,
                    updated_at=CURRENT_TIMESTAMP
            """, (task_id, platform, title, category, url, status, attempts,
                  result, failure_reason, next_action, metadata_str))
            conn.commit()

    def get_task(self, task_id: str) -> Optional[TaskRecord]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT task_id, platform, title, category, url, status, attempts,
                       result, failure_reason, next_action, metadata_json
                FROM tasks WHERE task_id = ?
            """, (task_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return TaskRecord(
                task_id=row[0], platform=row[1], title=row[2], category=row[3],
                url=row[4], status=row[5], attempts=row[6], result=row[7],
                failure_reason=row[8], next_action=row[9],
                metadata=json.loads(row[10] or "{}")
            )

    def get_pending_tasks(self, platform: Optional[str] = None) -> List[TaskRecord]:
        with sqlite3.connect(self.db_path) as conn:
            if platform:
                cursor = conn.execute("""
                    SELECT task_id, platform, title, category, url, status, attempts,
                           result, failure_reason, next_action, metadata_json
                    FROM tasks WHERE status IN ('pending', 'in_progress', 'redo') AND platform = ?
                    ORDER BY created_at ASC
                """, (platform,))
            else:
                cursor = conn.execute("""
                    SELECT task_id, platform, title, category, url, status, attempts,
                           result, failure_reason, next_action, metadata_json
                    FROM tasks WHERE status IN ('pending', 'in_progress', 'redo')
                    ORDER BY created_at ASC
                """)
            return [
                TaskRecord(
                    task_id=row[0], platform=row[1], title=row[2], category=row[3],
                    url=row[4], status=row[5], attempts=row[6], result=row[7],
                    failure_reason=row[8], next_action=row[9],
                    metadata=json.loads(row[10] or "{}")
                )
                for row in cursor.fetchall()
            ]

    def get_summary_stats(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status IN ('pending', 'in_progress', 'redo') THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN status = 'blocked' THEN 1 ELSE 0 END) as blocked
                FROM tasks
            """)
            row = cursor.fetchone()
            total = row[0] or 0
            completed = row[1] or 0
            pending = row[2] or 0
            blocked = row[3] or 0
            success_rate = (completed / total * 100.0) if total > 0 else 0.0
            return {
                "total_discovered": total,
                "total_completed": completed,
                "total_pending": pending,
                "total_blocked": blocked,
                "success_rate_percent": round(success_rate, 2),
            }

    def export_state_json(self, export_path: Optional[str] = None) -> str:
        target_path = export_path or "data/state_summary.json"
        os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
        stats = self.get_summary_stats()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM tasks")
            col_names = [d[0] for d in cursor.description]
            tasks = [dict(zip(col_names, row)) for row in cursor.fetchall()]
        data = {
            "summary": stats,
            "tasks": tasks,
            "exported_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return target_path


class ReferenceSandbox:
    """Subprocess test runner executing candidate solutions in isolation."""

    @staticmethod
    def validate_solution(
        code: str,
        sample_input: str,
        expected_output: str,
        timeout_sec: float = 3.0
    ) -> ValidationResult:
        start_time = time.time()
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tf:
            tf.write(code)
            temp_path = tf.name

        try:
            proc = subprocess.run(
                [sys.executable, temp_path],
                input=sample_input,
                capture_output=True,
                text=True,
                timeout=timeout_sec
            )
            duration_ms = (time.time() - start_time) * 1000.0
            actual_out = proc.stdout.strip()
            expected_out = expected_output.strip()
            passed = (proc.returncode == 0) and (actual_out == expected_out)
            err_msg = None if passed else (proc.stderr.strip() or f"Output mismatch: got '{actual_out}', expected '{expected_out}'")
            return ValidationResult(
                passed=passed,
                stdout=actual_out,
                stderr=proc.stderr.strip(),
                exit_code=proc.returncode,
                duration_ms=duration_ms,
                error_message=err_msg
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                passed=False,
                stdout="",
                stderr="TimeoutExpired",
                exit_code=-1,
                duration_ms=timeout_sec * 1000.0,
                error_message=f"Execution timed out after {timeout_sec} seconds"
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class ReferenceHITLHandler:
    """Canonical HITL guardrail handler detecting challenges and prompting user."""

    @staticmethod
    def check_guardrails_in_html(html_content: str) -> bool:
        """Returns True if human-intervention guardrail (MFA, CAPTCHA, modal) is present."""
        indicators = [
            "login-mfa-active",
            "login-mfa-wrapper",
            "cf-turnstile",
            "recaptcha",
            'id="myModal"',
            "Account disabled. Contact Coordinator.",
            "mfaRequired",
            "That's It! You Are Ready!"
        ]
        return any(ind in html_content for ind in indicators)

    @staticmethod
    def request_project_links(
        project_title: str,
        project_id: str,
        local_code_dir: str,
        required_fields: List[str],
        user_inputs: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Pauses and collects project repository & deployment URLs from user."""
        if user_inputs is not None:
            # Used in automated testing without blocking stdin
            return {k: user_inputs.get(k, f"https://mock.deployed/{k}") for k in required_fields}
        result = {}
        for field in required_fields:
            val = input(f"Enter {field}: ").strip()
            result[field] = val
        return result


class ReferenceReporter:
    """Canonical Markdown and JSON report generator."""

    @staticmethod
    def generate_report(
        stats: Dict[str, Any],
        tasks: List[TaskRecord],
        output_dir: str = "reports"
    ) -> Dict[str, str]:
        os.makedirs(output_dir, exist_ok=True)
        md_path = os.path.join(output_dir, "SUMMARY_REPORT.md")
        json_path = os.path.join(output_dir, "summary.json")

        # Generate Markdown
        md_lines = [
            "# Automation Execution Summary Report",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary Metrics",
            f"- **Total Discovered**: {stats.get('total_discovered', 0)}",
            f"- **Total Completed**: {stats.get('total_completed', 0)}",
            f"- **Total Pending**: {stats.get('total_pending', 0)}",
            f"- **Total Blocked**: {stats.get('total_blocked', 0)}",
            f"- **Success Rate**: {stats.get('success_rate_percent', 0.0)}%",
            "",
            "## Task Details",
            "| Task ID | Platform | Category | Title | Status | Attempts | Result |",
            "|---|---|---|---|---|---|---|"
        ]
        for t in tasks:
            md_lines.append(f"| {t.task_id} | {t.platform} | {t.category} | {t.title} | {t.status} | {t.attempts} | {t.result} |")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        # Generate JSON
        json_data = {
            "metrics": stats,
            "tasks": [t._asdict() for t in tasks],
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)

        return {"markdown": md_path, "json": json_path}
