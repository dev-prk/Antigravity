"""
core/reporter.py - Reporting Engine
Compiles executive Markdown reports, machine-readable JSON metrics, and CLI summaries
strictly adhering to Requirement R3:
total discovered, completed, pending, blocked, failed, success rate, time spent,
and issues requiring human intervention.
"""

from __future__ import annotations
import json
import os
import uuid
import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime, timezone

from core.state_manager import StateManager, TaskStatus, TaskRecord


class SummaryReporter:
    """
    Produces executive Markdown reports and machine-readable JSON summaries
    adhering strictly to Requirement R3:
    total discovered, completed, pending, blocked, failed, success rate,
    time spent, and issues requiring human intervention.
    """

    def __init__(
        self,
        state_manager: Optional[StateManager] = None,
        report_dir: str = "reports"
    ) -> None:
        self.state_manager = state_manager
        self.report_dir = Path(report_dir).resolve()
        self.report_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Formats seconds into HH:MM:SS or MM:SS."""
        total_secs = int(round(seconds))
        hours = total_secs // 3600
        minutes = (total_secs % 3600) // 60
        secs = total_secs % 60
        if hours > 0:
            return f"{hours:02d}h {minutes:02d}m {secs:02d}s"
        return f"{minutes:02d}m {secs:02d}s"

    def generate_markdown_report(self, output_file: Optional[str] = None) -> str:
        """
        Compiles and writes executive Markdown report (reports/SUMMARY_REPORT.md).
        Returns the absolute path to the generated file.
        """
        if self.state_manager is None:
            raise RuntimeError("StateManager instance required for generate_markdown_report()")

        target_path = Path(output_file or self.report_dir / "SUMMARY_REPORT.md").resolve()
        target_path.parent.mkdir(parents=True, exist_ok=True)

        stats = self.state_manager.get_summary_stats()
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Determine overall status badge
        if stats["total_blocked"] > 0:
            status_badge = "🟡 **ACTION REQUIRED — HUMAN INTERVENTION PENDING**"
        elif stats["total_failed"] > 0:
            status_badge = "🔴 **FAILED ITEMS REQUIRE ATTENTION**"
        elif stats["total_pending"] > 0:
            status_badge = "🔵 **EXECUTION IN PROGRESS / PARTIAL**"
        else:
            status_badge = "🟢 **ALL DISCOVERED ITEMS COMPLETED SUCCESSFULLY**"

        lines = [
            "# 📊 ZenClass & Guvi Automation Execution Summary Report",
            "",
            f"**Report Generated**: `{now_str}`  ",
            f"**Execution Status**: {status_badge}  ",
            "",
            "---",
            "",
            "## 1. Executive Summary",
            "",
            "| Metric | Value | Description |",
            "|---|---|---|",
            f"| **Total Tasks Discovered** | **{stats['total_discovered']}** | Total tasks identified across all platforms |",
            f"| **Total Tasks Completed** | **{stats['total_completed']}** | Verified successful submissions (`Solved!` / `Submitted`) |",
            f"| **Total Tasks Pending** | **{stats['total_pending']}** | Items awaiting execution |",
            f"| **Total Tasks In Progress** | **{stats['total_in_progress']}** | Currently active tasks |",
            f"| **Total Tasks Blocked** | **{stats['total_blocked']}** | Halted items requiring human intervention |",
            f"| **Total Tasks Failed** | **{stats['total_failed']}** | Submissions failed after retries |",
            f"| **Overall Success Rate** | **{stats['success_rate_percent']:.1f}%** | Completed / Discovered percentage |",
            f"| **Total Time Spent** | **{self._format_duration(stats['total_time_spent_seconds'])}** | Cumulative automation runtime |",
            "",
            "---",
            "",
            "## 2. Platform Breakdown Matrix",
            "",
            "| Platform | Discovered | Completed | Pending | Blocked | Failed | Success Rate | Time Spent |",
            "|---|---|---|---|---|---|---|---|"
        ]

        by_platform = stats.get("by_platform", {})
        if not by_platform:
            lines.append("| *None* | 0 | 0 | 0 | 0 | 0 | 0.0% | 00m 00s |")
        else:
            for plat_name, pstats in by_platform.items():
                nice_name = plat_name.replace("_", " ").title()
                p_time = self._format_duration(pstats["time_spent_seconds"])
                lines.append(
                    f"| **{nice_name}** | {pstats['total_discovered']} | "
                    f"{pstats['total_completed']} | {pstats['total_pending']} | "
                    f"{pstats['total_blocked']} | {pstats['total_failed']} | "
                    f"**{pstats['success_rate_percent']:.1f}%** | {p_time} |"
                )

        # Totals row in platform table
        total_time_str = self._format_duration(stats["total_time_spent_seconds"])
        lines.append(
            f"| **TOTAL** | **{stats['total_discovered']}** | "
            f"**{stats['total_completed']}** | **{stats['total_pending']}** | "
            f"**{stats['total_blocked']}** | **{stats['total_failed']}** | "
            f"**{stats['success_rate_percent']:.1f}%** | **{total_time_str}** |"
        )

        lines.extend([
            "",
            "---",
            "",
            "## 3. 🚨 Human Intervention Required (Requirement R3)",
            ""
        ])

        human_issues = stats.get("human_intervention_issues", [])
        blocked_issues = [i for i in human_issues if i.get("status") in ("BLOCKED", "blocked") or i.get("failure_reason")]

        if not blocked_issues:
            lines.extend([
                "✅ **No issues requiring human intervention!** All tasks are either completed or running smoothly without security blocks.",
                ""
            ])
        else:
            lines.extend([
                "> **Notice**: The following tasks encountered security checks (CAPTCHA/MFA) or external link requirements (GitHub/Vercel) and have been paused cleanly to prevent unauthorized bypass or fabricated data.",
                "",
                "| # | Platform | Task ID / Title | Status | Attempts | Failure Reason | Prescribed Action |",
                "|---|---|---|---|---|---|---|"
            ])
            for idx, issue in enumerate(blocked_issues, 1):
                p_label = issue["platform"].replace("_", " ").title()
                f_reason = (issue["failure_reason"] or "N/A").replace("|", "\\|")
                next_act = (issue["next_action"] or "Review required").replace("|", "\\|")
                lines.append(
                    f"| {idx} | `{p_label}` | **{issue['title']}** (`{issue['task_id']}`) | "
                    f"`{issue['status']}` | {issue['attempts']} | {f_reason} | {next_act} |"
                )
            lines.append("")

        lines.extend([
            "---",
            "",
            "## 4. Category Breakdown",
            "",
            "| Category | Total Items | Completed | Success Rate |",
            "|---|---|---|---|"
        ])

        by_cat = stats.get("by_category", {})
        if not by_cat:
            lines.append("| *None* | 0 | 0 | 0.0% |")
        else:
            for cat_name, cstats in sorted(by_cat.items(), key=lambda x: x[0]):
                lines.append(
                    f"| `{cat_name}` | {cstats['total']} | {cstats['completed']} | "
                    f"{cstats['success_rate_percent']:.1f}% |"
                )

        lines.extend([
            "",
            "---",
            "",
            "## 5. Recent Task Executions",
            "",
            "| Timestamp | Platform | Task Title | Status | Result | Duration | Attempts |",
            "|---|---|---|---|---|---|---|"
        ])

        # Get last 10 tasks sorted by updated_at desc
        all_tasks = self.state_manager.list_tasks()
        recent_tasks = sorted(all_tasks, key=lambda t: t.updated_at, reverse=True)[:10]

        if not recent_tasks:
            lines.append("| *No task execution history recorded yet.* | - | - | - | - | - | - |")
        else:
            for t in recent_tasks:
                ts = t.updated_at[:19].replace("T", " ")
                plat_short = t.platform.replace("_", " ").title()
                dur_str = f"{t.time_spent_seconds:.1f}s" if t.time_spent_seconds > 0 else "-"
                lines.append(
                    f"| {ts} | {plat_short} | {t.title} | `{t.status}` | `{t.result}` | {dur_str} | {t.attempt_count} |"
                )

        lines.extend([
            "",
            "---",
            "*Report generated autonomously by ZenClass & Guvi Automation Suite.*",
            ""
        ])

        report_content = "\n".join(lines)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        return str(target_path)

    def generate_json_report(self, output_file: Optional[str] = None) -> str:
        """
        Compiles and writes reports/summary.json atomically.
        Returns the absolute path to the generated file.
        """
        if self.state_manager is None:
            raise RuntimeError("StateManager instance required for generate_json_report()")

        target_path = Path(output_file or self.report_dir / "summary.json").resolve()
        target_path.parent.mkdir(parents=True, exist_ok=True)

        temp_path = target_path.with_name(
            f"{target_path.name}.tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}"
        )

        stats = self.state_manager.get_summary_stats()
        payload = {
            "schema_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary_metrics": {
                "total_discovered": stats["total_discovered"],
                "total_completed": stats["total_completed"],
                "total_pending": stats["total_pending"],
                "total_in_progress": stats["total_in_progress"],
                "total_blocked": stats["total_blocked"],
                "total_failed": stats["total_failed"],
                "success_rate_percent": stats["success_rate_percent"],
                "total_time_spent_seconds": stats["total_time_spent_seconds"],
                "formatted_time_spent": self._format_duration(stats["total_time_spent_seconds"])
            },
            "by_platform": stats.get("by_platform", {}),
            "by_category": stats.get("by_category", {}),
            "human_intervention_issues": stats.get("human_intervention_issues", [])
        }

        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_path, target_path)
        return str(target_path)

    def generate_all_reports(self) -> Tuple[str, str]:
        """Generates both Markdown and JSON reports, returning (md_path, json_path)."""
        md = self.generate_markdown_report()
        js = self.generate_json_report()
        return md, js

    def print_terminal_summary(self) -> None:
        """Prints a high-impact formatted summary card to standard output."""
        if self.state_manager is None:
            return

        stats = self.state_manager.get_summary_stats()
        time_str = self._format_duration(stats["total_time_spent_seconds"])

        print("\n" + "=" * 70)
        print("          ZENCLASS & GUVI CODEKATA EXECUTION SUMMARY")
        print("=" * 70)
        print(f" Total Discovered : {stats['total_discovered']:<6} | Total Completed : {stats['total_completed']:<6}")
        print(f" Total Pending    : {stats['total_pending']:<6} | Total In-Progress: {stats['total_in_progress']:<6}")
        print(f" Total Blocked    : {stats['total_blocked']:<6} | Total Failed    : {stats['total_failed']:<6}")
        print(f" Success Rate     : {stats['success_rate_percent']:.1f}% | Total Time Spent: {time_str}")
        print("-" * 70)

        issues = stats.get("human_intervention_issues", [])
        if issues:
            print(f" ⚠️  HUMAN INTERVENTION REQUIRED: {len(issues)} item(s) paused")
            for item in issues[:3]:
                print(f"   - [{item['platform']}] {item['title']}: {item['failure_reason']}")
            if len(issues) > 3:
                print(f"   ... and {len(issues) - 3} more (see reports/SUMMARY_REPORT.md)")
        else:
            print(" ✅ No human interventions required. All items clear.")
        print("=" * 70 + "\n")

    @classmethod
    def generate_report(
        cls,
        stats: Dict[str, Any],
        tasks: List[Any],
        output_dir: str = "reports"
    ) -> Dict[str, str]:
        """
        Direct functional API for test harness compatibility (test_f04_reporter.py).
        Writes SUMMARY_REPORT.md and summary.json to output_dir and returns paths dict.
        """
        out_p = Path(output_dir).resolve()
        out_p.mkdir(parents=True, exist_ok=True)
        md_path = out_p / "SUMMARY_REPORT.md"
        json_path = out_p / "summary.json"

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
            t_id = getattr(t, "task_id", t.get("task_id", "") if isinstance(t, dict) else "")
            plat = getattr(t, "platform", t.get("platform", "") if isinstance(t, dict) else "")
            cat = getattr(t, "category", getattr(t, "task_category", t.get("category", "") if isinstance(t, dict) else ""))
            title = getattr(t, "title", t.get("title", "") if isinstance(t, dict) else "")
            status = getattr(t, "status", t.get("status", "") if isinstance(t, dict) else "")
            attempts = getattr(t, "attempts", getattr(t, "attempt_count", t.get("attempts", 0) if isinstance(t, dict) else 0))
            result = getattr(t, "result", t.get("result", "") if isinstance(t, dict) else "")
            md_lines.append(f"| {t_id} | {plat} | {cat} | {title} | {status} | {attempts} | {result} |")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        # Generate JSON
        json_tasks = []
        for t in tasks:
            if hasattr(t, "_asdict"):
                json_tasks.append(t._asdict())
            elif hasattr(t, "to_dict"):
                json_tasks.append(t.to_dict())
            elif isinstance(t, dict):
                json_tasks.append(t)
            else:
                json_tasks.append(str(t))

        json_data = {
            "metrics": stats,
            "tasks": json_tasks,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)

        return {"markdown": str(md_path), "json": str(json_path)}


# Alias for contract loader and test compatibility
Reporter = SummaryReporter
