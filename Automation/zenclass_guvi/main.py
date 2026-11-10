"""
main.py - ZenClass & Guvi CodeKata Automation Suite Unified CLI Entrypoint

Commands:
  run-all         Execute Guvi CodeKata, ZenClass tasks, and ZenClass projects
  run-codekata    Execute Guvi CodeKata automation only
  run-zenclass    Execute ZenClass automation (tasks, projects, or both)
  run-zenclass-tasks Execute ZenClass tasks automation only
  resume          Resume execution from saved SQLite state (pending/blocked items)
  report          Generate Markdown & JSON summary reports without launching browser
"""

from __future__ import annotations
import argparse
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import List, Optional

import config
from core.browser import BrowserManager
from core.state_manager import StateManager
from core.hitl_handler import HitlHandler
from core.reporter import SummaryReporter

logger = logging.getLogger("zenclass_guvi")


def setup_logging(level_name: str = "INFO") -> None:
    """Configures structured, colored CLI logging."""
    level = getattr(logging, level_name.upper(), logging.INFO)
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(level=level, format=fmt, datefmt="%H:%M:%S")


def create_cli_parser() -> argparse.ArgumentParser:
    """Constructs the argument parser with subcommands and options."""
    parser = argparse.ArgumentParser(
        prog="zenclass_guvi",
        description="Autonomous ZenClass & Guvi CodeKata Automation Suite (R1, R2, R3)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global options
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode (default: False, headed foreground as per R1)",
    )
    parser.add_argument(
        "--slow-mo",
        type=float,
        default=50.0,
        help="Playwright slow_mo delay in milliseconds (default: 50ms)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of problems/tasks to attempt in this run",
    )
    parser.add_argument(
        "--interactive",
        dest="interactive",
        action="store_true",
        default=True,
        help="Enable interactive terminal prompts for CAPTCHA/MFA and project URLs (default: True)",
    )
    parser.add_argument(
        "--no-interactive",
        dest="interactive",
        action="store_false",
        help="Disable interactive terminal prompts (mark HITL tasks as blocked)",
    )
    parser.add_argument(
        "--links-file",
        type=str,
        default=None,
        help="Path to JSON file containing pre-filled repository and deployment links",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default=str(config.DB_PATH),
        help="Path to SQLite persistent state tracking database",
    )
    parser.add_argument(
        "--reports-dir",
        type=str,
        default=str(config.REPORTS_DIR),
        help="Directory to write executive Markdown and JSON reports",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging verbosity level (default: INFO)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Automation commands")

    # Command: run-all
    p_run_all = subparsers.add_parser(
        "run-all",
        help="Run full automation pipeline across Guvi CodeKata, ZenClass tasks, and projects",
    )
    p_run_all.add_argument(
        "--order",
        choices=["codekata-first", "zenclass-first"],
        default="codekata-first",
        help="Execution order between platforms (default: codekata-first)",
    )

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

    # Command: run-zenclass
    p_zenclass = subparsers.add_parser(
        "run-zenclass",
        help="Run ZenClass tasks and/or projects automation",
    )
    p_zenclass.add_argument(
        "--type",
        choices=["tasks", "projects", "all"],
        default="all",
        help="Scope of ZenClass automation: tasks, projects, or all (default: all)",
    )
    p_zenclass.add_argument(
        "--task-id",
        type=str,
        default=None,
        help="Execute single ZenClass task or project by ID",
    )

    # Command: run-zenclass-tasks
    p_zenclass_tasks = subparsers.add_parser(
        "run-zenclass-tasks",
        help="Run ZenClass tasks automation (discovery, dynamic modal submission, verification)",
    )
    p_zenclass_tasks.add_argument(
        "--task-id",
        type=str,
        default=None,
        help="Execute single ZenClass task by ID",
    )

    # Command: resume
    p_resume = subparsers.add_parser(
        "resume",
        help="Resume execution from SQLite state for pending, failed, or blocked tasks",
    )
    p_resume.add_argument(
        "--platform",
        choices=["all", "guvi", "zenclass"],
        default="all",
        help="Filter platform to resume (default: all)",
    )
    p_resume.add_argument(
        "--include-failed",
        action="store_true",
        default=True,
        help="Retry failed tasks in addition to pending/blocked tasks (default: True)",
    )

    # Command: report
    subparsers.add_parser(
        "report",
        help="Generate Markdown & JSON summary reports from database without launching browser",
    )

    return parser


class AutomationRunner:
    """Lifecycle controller managing browser, state, drivers, and shutdown signals."""

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.browser_manager: Optional[BrowserManager] = None
        self.state_manager: Optional[StateManager] = None
        self.hitl_handler: Optional[HitlHandler] = None
        self.reporter: Optional[SummaryReporter] = None
        self._run_id: Optional[str] = None
        self._shutdown_registered = False

    def register_signal_handlers(self) -> None:
        """Gracefully catches SIGINT (Ctrl+C) and SIGTERM."""
        def handle_signal(signum, frame):
            print("\n\033[1;33m[SHUTDOWN] Interrupt signal caught. Gracefully saving state and closing browser...\033[0m")
            self.cleanup()
            sys.exit(130)

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
        self._shutdown_registered = True

    def initialize_services(self) -> None:
        """Initializes configuration, state database, HITL handler, and reporting."""
        setup_logging(self.args.log_level)
        self.register_signal_handlers()

        self.state_manager = StateManager(
            db_path=self.args.db_path,
            json_export_path=str(Path(self.args.db_path).parent / "state_summary.json")
        )
        self.hitl_handler = HitlHandler(
            interactive=self.args.interactive,
            state_manager=self.state_manager,
            links_file=self.args.links_file,
        )
        self.reporter = SummaryReporter(
            state_manager=self.state_manager,
            report_dir=self.args.reports_dir,
        )
        logger.info(f"Initialized state tracking database: {self.args.db_path}")

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

    def cleanup(self) -> None:
        """Flushes state and closes browser profile cleanly."""
        try:
            if self.browser_manager:
                logger.info("Closing browser context (preserving cookies and profile)...")
                self.browser_manager.close()
                self.browser_manager = None
            if self.state_manager:
                logger.info("Exporting atomic JSON state summary...")
                self.state_manager.export_state_json()
                if self._run_id:
                    self.state_manager.end_execution_run(self._run_id, status="COMPLETED")
                self.state_manager.close()
                self.state_manager = None
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def execute(self) -> int:
        """Dispatches command to relevant drivers and produces summary report."""
        if not self.args.command:
            print("No command specified. Use --help for usage instructions.")
            return 1

        self.initialize_services()

        # Fast path: report-only does not require browser initialization
        if self.args.command == "report":
            logger.info("Generating summary reports from state database...")
            md_path, json_path = self.reporter.generate_all_reports()
            self.reporter.print_terminal_summary()
            print(f"Reports generated successfully:\n  - Markdown: {md_path}\n  - JSON: {json_path}")
            return 0

        # Launch headed browser for automation commands
        try:
            self._run_id = self.state_manager.start_execution_run(
                command=self.args.command,
                platform_filter=getattr(self.args, "platform", None)
            )

            self.initialize_browser()

            if self.args.command == "run-all":
                logger.info("Executing run-all automation pipeline across Guvi and ZenClass...")
                from drivers.guvi_driver import GuviDriver
                from drivers.zenclass_tasks_driver import ZenClassTasksDriver

                order = getattr(self.args, "order", "codekata-first")
                if order == "zenclass-first":
                    tasks_driver = ZenClassTasksDriver(
                        browser_manager=self.browser_manager,
                        state_manager=self.state_manager,
                        hitl_handler=self.hitl_handler,
                        reporter=self.reporter,
                    )
                    tasks_driver.run_task_pipeline(limit=self.args.limit)

                    guvi_driver = GuviDriver(
                        browser_manager=self.browser_manager,
                        state_manager=self.state_manager,
                        hitl_handler=self.hitl_handler,
                        reporter=self.reporter,
                    )
                    guvi_driver.run_pipeline(limit=self.args.limit)
                else:
                    guvi_driver = GuviDriver(
                        browser_manager=self.browser_manager,
                        state_manager=self.state_manager,
                        hitl_handler=self.hitl_handler,
                        reporter=self.reporter,
                    )
                    guvi_driver.run_pipeline(limit=self.args.limit)

                    tasks_driver = ZenClassTasksDriver(
                        browser_manager=self.browser_manager,
                        state_manager=self.state_manager,
                        hitl_handler=self.hitl_handler,
                        reporter=self.reporter,
                    )
                    tasks_driver.run_task_pipeline(limit=self.args.limit)
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
            elif self.args.command == "run-zenclass-tasks":
                logger.info(f"Executing ZenClass tasks automation (limit={self.args.limit}, task_id={self.args.task_id})...")
                from drivers.zenclass_tasks_driver import ZenClassTasksDriver
                tasks_driver = ZenClassTasksDriver(
                    browser_manager=self.browser_manager,
                    state_manager=self.state_manager,
                    hitl_handler=self.hitl_handler,
                    reporter=self.reporter,
                )
                tasks_driver.run_task_pipeline(
                    limit=self.args.limit,
                    task_id=self.args.task_id,
                )
            elif self.args.command == "run-zenclass":
                logger.info(f"Executing ZenClass automation (type={self.args.type}, limit={self.args.limit})...")
                if getattr(self.args, "type", "all") in ("tasks", "all"):
                    from drivers.zenclass_tasks_driver import ZenClassTasksDriver
                    tasks_driver = ZenClassTasksDriver(
                        browser_manager=self.browser_manager,
                        state_manager=self.state_manager,
                        hitl_handler=self.hitl_handler,
                        reporter=self.reporter,
                    )
                    tasks_driver.run_task_pipeline(
                        limit=self.args.limit,
                        task_id=self.args.task_id,
                    )
            elif self.args.command == "resume":
                logger.info(f"Resuming automation from state database (platform={self.args.platform})...")

            # Generate final reports upon execution completion
            if self.reporter:
                self.reporter.generate_all_reports()
                self.reporter.print_terminal_summary()

            return 0

        except Exception as e:
            logger.exception(f"Unhandled error during execution: {e}")
            return 1
        finally:
            self.cleanup()


def main() -> None:
    parser = create_cli_parser()
    args = parser.parse_args()
    runner = AutomationRunner(args)
    sys.exit(runner.execute())


if __name__ == "__main__":
    main()
