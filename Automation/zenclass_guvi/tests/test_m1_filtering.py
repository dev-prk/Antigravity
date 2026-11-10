"""
tests/test_m1_filtering.py - Comprehensive Unit and Integration Tests for Milestone 1

Covers:
1. StateManager.list_pending and get_pending_tasks difficulty filtering:
   - None / empty list (backward compatibility)
   - Single difficulty ('Medium')
   - Multiple difficulties (['Medium', 'Hard'])
   - Case-insensitivity ('medium', 'HARD')
   - Whitespace stripping ('  Medium  ')
   - Unknown difficulty handling
   - Exclusion of non-matching or missing difficulty metadata
   - Crash-proof SQLite queries with malformed/non-JSON or null metadata
   - Combination with platform, limit, and status filters
2. Extractor CSS Sanitization:
   - Unclosed and spaced style tags (</style >, </ style>, unclosed <style>)
   - CSS declaration block sanitization in sample inputs/outputs
   - Ignoring bare CSS input/output selectors (input { display: inline-flex; })
   - Preservation of legitimate JSON, Python dicts, sets, and code blocks
   - Stripping of CSS comments (/* ... */)
   - Multiple sample cases with bogus CSS cases discarded and valid cases renumbered
   - Handling CSS @media at-rules
3. Config and CLI:
   - Config constants (HEADLESS, CODEKATA_HEADLESS, DEFAULT_CODEKATA_DIFFICULTIES, VALID_CODEKATA_DIFFICULTIES)
   - CLI argument parsing: --headless, --no-headless, --headed (root and subparsers)
   - Command-specific headless defaults (run-codekata -> True, run-zenclass -> False)
   - CLI --difficulty parsing (comma-separated, repeated, case normalization)
   - parse_difficulties helper behavior and validation
   - AutomationRunner driver kwargs propagation (preserving mock compatibility)
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import config
from core.state_manager import StateManager, TaskRecord
from main import AutomationRunner, create_cli_parser, parse_difficulties
from solver.extractor import ProblemExtractor, SampleCase


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
            metadata={"difficulty": "Easy", "slug": "easy-1"},
        )
        # 2. Medium Guvi task (discovered)
        self.sm.record_task(
            task_id="guvi-med-1",
            platform="guvi",
            title="Problem Medium 1",
            category="CodeKata",
            status="discovered",
            metadata={"difficulty": "Medium", "slug": "med-1"},
        )
        # 3. Hard Guvi task (redo, uppercase difficulty)
        self.sm.record_task(
            task_id="guvi-hard-1",
            platform="guvi",
            title="Problem Hard 1",
            category="CodeKata",
            status="redo",
            metadata={"difficulty": "HARD", "slug": "hard-1"},
        )
        # 4. Completed Medium Guvi task (must be filtered out by status)
        self.sm.record_task(
            task_id="guvi-med-completed",
            platform="guvi",
            title="Problem Medium Completed",
            category="CodeKata",
            status="completed",
            metadata={"difficulty": "Medium", "slug": "med-comp"},
        )
        # 5. ZenClass task with no difficulty (pending)
        self.sm.record_task(
            task_id="zen-task-1",
            platform="zenclass",
            title="ZenClass Task 1",
            category="Tasks",
            status="pending",
            metadata={"tags": ["javascript"]},
        )
        # 6. Task with empty metadata dict (pending)
        self.sm.record_task(
            task_id="empty-meta-1",
            platform="guvi",
            title="Empty Meta Task",
            category="CodeKata",
            status="pending",
            metadata={},
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
        self.sm.conn.commit()
        # Should not raise sqlite3.OperationalError: malformed JSON
        tasks = self.sm.list_pending(difficulties=["Medium"])
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_id, "guvi-med-1")

    def test_13_null_and_empty_metadata_resilience(self):
        """Tasks with NULL or empty string metadata are cleanly ignored without error."""
        cursor = self.sm.conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (task_id, platform, task_category, title, status, metadata, created_at, updated_at) "
            "VALUES ('null-meta-task', 'guvi', 'CodeKata', 'Null Task', 'pending', NULL, '2026-01-01', '2026-01-01');"
        )
        cursor.execute(
            "INSERT INTO tasks (task_id, platform, task_category, title, status, metadata, created_at, updated_at) "
            "VALUES ('empty-str-meta-task', 'guvi', 'CodeKata', 'Empty Str Task', 'pending', '', '2026-01-01', '2026-01-01');"
        )
        self.sm.conn.commit()
        tasks = self.sm.list_pending(difficulties=["Medium"])
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_id, "guvi-med-1")


class TestExtractorCSSSanitization(unittest.TestCase):
    """Verifies that ProblemExtractor eliminates CSS leaks while preserving legitimate code and inputs."""

    def test_01_sanitizes_unclosed_and_spaced_style_tags(self):
        """Strips <style> blocks with spaced closing tags and unclosed style tags."""
        html = """
        <div>
            <style type="text/css" >
                input { display: inline-flex; font-size: inherit; }
            </style >
            <style>
                .ace_editor { position: relative; }
            </ style>
            <h1>Sum of Two Numbers</h1>
            <p>Problem Statement: Given two integers, print their sum.</p>
            <style>
                body { margin: 0; padding: 0; }
            <p>Sample Input: 3 5</p>
            <p>Sample Output: 8</p>
        </div>
        """
        spec = ProblemExtractor.extract(html)
        self.assertEqual(spec.title, "Sum of Two Numbers")
        self.assertNotIn("display: inline-flex", spec.raw_text)
        self.assertNotIn("position: relative", spec.raw_text)
        self.assertEqual(spec.sample_input, "3 5")
        self.assertEqual(spec.sample_output, "8")

    def test_02_sanitizes_css_declaration_block_in_sample_input(self):
        """Strips inline CSS declaration block contaminating sample input text."""
        html = """
        <div>
            <h1>Prime Check</h1>
            <p>Sample Input: {display:inline-flex;font-size:inherit;line-height:inherit;flex:1}\n7</p>
            <p>Sample Output: yes</p>
        </div>
        """
        spec = ProblemExtractor.extract(html)
        self.assertEqual(spec.sample_input, "7")
        self.assertEqual(spec.sample_output, "yes")

    def test_03_ignores_css_input_output_element_selectors(self):
        """Prevents CSS rules like 'input { display: ... } output { ... }' from becoming sample cases."""
        html = """
        <div>
            <h1>Even Check</h1>
            <p>Given an integer N, print even or odd.</p>
            input {display:inline-flex;font-size:inherit;line-height:inherit;flex:1;}
            output {display:block;margin:0;}
            <p>Sample Input: 4</p>
            <p>Sample Output: even</p>
        </div>
        """
        spec = ProblemExtractor.extract(html)
        self.assertEqual(len(spec.sample_cases), 1)
        self.assertEqual(spec.sample_input, "4")
        self.assertEqual(spec.sample_output, "even")

    def test_04_preserves_legitimate_json_and_sets(self):
        """Preserves legitimate JSON inputs/outputs and Python sets containing property-like words."""
        html = """
        <div>
            <h1>JSON Parser Problem</h1>
            <p>Sample Input: {"display": "inline-flex", "count": 2}</p>
            <p>Sample Output: {1, 2, 3}</p>
        </div>
        """
        spec = ProblemExtractor.extract(html)
        self.assertEqual(len(spec.sample_cases), 1)
        self.assertEqual(spec.sample_input, '{"display": "inline-flex", "count": 2}')
        self.assertEqual(spec.sample_output, "{1, 2, 3}")

    def test_05_preserves_code_snippets_with_braces(self):
        """Preserves C and Python code blocks containing braces and returns."""
        html = """
        <div>
            <h1>Code Execution Problem</h1>
            <p>Sample Input: { int x = 10; return x * 2; }</p>
            <p>Sample Output: 20</p>
        </div>
        """
        spec = ProblemExtractor.extract(html)
        self.assertEqual(len(spec.sample_cases), 1)
        self.assertEqual(spec.sample_input, "{ int x = 10; return x * 2; }")
        self.assertEqual(spec.sample_output, "20")

    def test_06_sanitizes_css_comments(self):
        """Strips CSS comments (/* ... */) preventing slash/star leakage into numbers."""
        html = """
        <div>
            <h1>Comment Test</h1>
            <p>Sample Input: /* layout rule */ 42</p>
            <p>Sample Output: 84</p>
        </div>
        """
        spec = ProblemExtractor.extract(html)
        self.assertEqual(spec.sample_input, "42")
        self.assertEqual(spec.sample_output, "84")

    def test_07_multi_case_with_bogus_css_first(self):
        """Discards a bogus CSS case at index 0 and correctly renumbers subsequent valid cases."""
        # Simulate text where a CSS rule preceded legitimate sample test cases
        html = """
        <div>
            <h1>Multi Test</h1>
            input {display:inline-flex;}
            output {display:none;}
            <p>Sample Input Case 1: 10</p>
            <p>Sample Output Case 1: 20</p>
            <p>Sample Input Case 2: 30</p>
            <p>Sample Output Case 2: 60</p>
        </div>
        """
        spec = ProblemExtractor.extract(html)
        self.assertEqual(len(spec.sample_cases), 2)
        self.assertEqual(spec.sample_cases[0].case_number, 1)
        self.assertEqual(spec.sample_cases[0].input_text, "10")
        self.assertEqual(spec.sample_cases[0].expected_output, "20")
        self.assertEqual(spec.sample_cases[1].case_number, 2)
        self.assertEqual(spec.sample_cases[1].input_text, "30")
        self.assertEqual(spec.sample_cases[1].expected_output, "60")

    def test_08_sanitizes_media_queries_and_at_rules(self):
        """Strips @media queries and @keyframes declarations from description text."""
        html = """
        <div>
            <h1>Responsive Problem</h1>
            @media screen and (max-width: 600px) { body { font-size: 12px; } }
            <p>Problem Statement: Count words in text.</p>
            <p>Sample Input: hello world</p>
            <p>Sample Output: 2</p>
        </div>
        """
        spec = ProblemExtractor.extract(html)
        self.assertNotIn("@media", spec.raw_text)
        self.assertNotIn("font-size: 12px", spec.raw_text)
        self.assertEqual(spec.sample_input, "hello world")
        self.assertEqual(spec.sample_output, "2")


class TestCliAndConfigSettings(unittest.TestCase):
    """Verifies config constants and CLI argument parsing behavior."""

    def test_01_config_constants(self):
        """Verifies HEADLESS default is False, CODEKATA_HEADLESS default is True, and difficulty lists exist."""
        self.assertFalse(config.HEADLESS, "config.HEADLESS must default to False for legacy compatibility")
        self.assertTrue(config.CODEKATA_HEADLESS, "config.CODEKATA_HEADLESS must default to True")
        self.assertEqual(config.DEFAULT_CODEKATA_DIFFICULTIES, ["Medium", "Hard"])
        self.assertEqual(config.VALID_CODEKATA_DIFFICULTIES, ["Easy", "Medium", "Hard"])

        # Also exposed on Config class
        self.assertFalse(config.Config.HEADLESS)
        self.assertTrue(config.Config.CODEKATA_HEADLESS)
        self.assertEqual(config.Config.DEFAULT_CODEKATA_DIFFICULTIES, ["Medium", "Hard"])
        self.assertEqual(config.Config.VALID_CODEKATA_DIFFICULTIES, ["Easy", "Medium", "Hard"])

    def test_02_cli_parser_headless_defaults(self):
        """Verifies run-codekata defaults to headless=True, whereas other commands default to headless=False."""
        parser = create_cli_parser()

        args_codekata = parser.parse_args(["run-codekata"])
        self.assertTrue(args_codekata.headless, "run-codekata must default to headless=True")

        args_zenclass = parser.parse_args(["run-zenclass"])
        self.assertFalse(args_zenclass.headless, "run-zenclass must default to headless=False")

        args_root = parser.parse_args([])
        self.assertFalse(args_root.headless, "root parser must default to headless=False")

    def test_03_cli_parser_no_headless_and_headed_flags(self):
        """Verifies --no-headless and --headed override headless mode both before and after subcommand."""
        parser = create_cli_parser()

        # Flag after subcommand
        self.assertFalse(parser.parse_args(["run-codekata", "--no-headless"]).headless)
        self.assertFalse(parser.parse_args(["run-codekata", "--headed"]).headless)
        self.assertTrue(parser.parse_args(["run-codekata", "--headless"]).headless)

        # Flag before subcommand
        self.assertFalse(parser.parse_args(["--no-headless", "run-codekata"]).headless)
        self.assertFalse(parser.parse_args(["--headed", "run-codekata"]).headless)
        self.assertTrue(parser.parse_args(["--headless", "run-codekata"]).headless)

    def test_04_parse_difficulties_helper(self):
        """Verifies parse_difficulties normalizes inputs into Title Case list."""
        self.assertEqual(parse_difficulties(["Medium,Hard"]), ["Medium", "Hard"])
        self.assertEqual(parse_difficulties(["Medium", "Hard"]), ["Medium", "Hard"])
        self.assertEqual(parse_difficulties("medium, hard"), ["Medium", "Hard"])
        self.assertEqual(parse_difficulties("Hard"), ["Hard"])
        self.assertEqual(parse_difficulties("EASY, medium"), ["Easy", "Medium"])

        # Edge cases: empty, None, invalid
        self.assertIsNone(parse_difficulties(None))
        self.assertIsNone(parse_difficulties([]))
        self.assertIsNone(parse_difficulties(["", "   "]))
        self.assertIsNone(parse_difficulties(["Unknown", "Expert"]))

    def test_05_cli_parser_difficulty_options(self):
        """Verifies --difficulty argument parsing on run-codekata and run-all."""
        parser = create_cli_parser()

        # Comma-separated on run-codekata
        args1 = parser.parse_args(["run-codekata", "--difficulty", "Medium,Hard"])
        self.assertEqual(parse_difficulties(args1.difficulty), ["Medium", "Hard"])

        # Repeated flags on run-codekata
        args2 = parser.parse_args(["run-codekata", "--difficulty", "Medium", "--difficulty", "Hard"])
        self.assertEqual(parse_difficulties(args2.difficulty), ["Medium", "Hard"])

        # run-all difficulty
        args3 = parser.parse_args(["run-all", "--difficulty", "Hard"])
        self.assertEqual(parse_difficulties(args3.difficulty), ["Hard"])

        # Omitted difficulty is None
        args4 = parser.parse_args(["run-codekata"])
        self.assertIsNone(args4.difficulty)

    @patch("drivers.guvi_driver.GuviDriver.run_pipeline")
    def test_06_main_runner_wires_difficulty_when_specified(self, mock_run_pipeline):
        """Verifies AutomationRunner passes difficulties to GuviDriver when specified."""
        parser = create_cli_parser()
        args = parser.parse_args(["run-codekata", "--difficulty", "Medium,Hard", "--limit", "2"])

        runner = AutomationRunner(args)
        runner.initialize_services = MagicMock()
        runner.initialize_browser = MagicMock()
        runner.cleanup = MagicMock()
        runner.state_manager = MagicMock(spec=StateManager)
        runner.reporter = MagicMock()

        exit_code = runner.execute()
        self.assertEqual(exit_code, 0)
        mock_run_pipeline.assert_called_once_with(
            limit=2,
            category=None,
            task_id=None,
            difficulties=["Medium", "Hard"],
        )

    @patch("drivers.guvi_driver.GuviDriver.run_pipeline")
    def test_07_main_runner_omits_difficulty_when_not_specified(self, mock_run_pipeline):
        """Verifies AutomationRunner omits difficulties from GuviDriver call when not specified (regression protection)."""
        parser = create_cli_parser()
        args = parser.parse_args(["run-codekata", "--limit", "3", "--category", "Basics"])

        runner = AutomationRunner(args)
        runner.initialize_services = MagicMock()
        runner.initialize_browser = MagicMock()
        runner.cleanup = MagicMock()
        runner.state_manager = MagicMock(spec=StateManager)
        runner.reporter = MagicMock()

        exit_code = runner.execute()
        self.assertEqual(exit_code, 0)
        mock_run_pipeline.assert_called_once_with(
            limit=3,
            category="Basics",
            task_id=None,
        )


if __name__ == "__main__":
    unittest.main()
