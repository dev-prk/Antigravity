"""
Tier 2 Boundary Tests: Special Characters and Escaping Integrity.
Verifies safety against SQL injection, quote escaping, multiline syntax, and Unicode.
"""

import unittest
from tests.e2e.harness.contract_loader import get_state_manager, get_sandbox


class TestBoundarySpecialCharsEscaping(unittest.TestCase):
    """Verifies encoding and escaping integrity across state storage and code synthesis."""

    def setUp(self):
        self.state_mgr, _ = get_state_manager(":memory:")
        self.sandbox, _ = get_sandbox()

    def test_sql_injection_resilience_in_state_manager(self):
        """Verifies parameterized queries prevent SQL injection payloads in all fields."""
        malicious_id = "test'; DROP TABLE tasks; --"
        malicious_title = "1' OR '1'='1"
        malicious_reason = "\"; DELETE FROM tasks WHERE 'a'='a"

        self.state_mgr.record_task(
            task_id=malicious_id,
            platform="guvi",
            title=malicious_title,
            category="CodeKata",
            url="https://guvi.in/test",
            status="pending",
            attempts=1,
            result="None",
            failure_reason=malicious_reason,
            next_action="retry"
        )

        task = self.state_mgr.get_task(malicious_id)
        self.assertIsNotNone(task)
        self.assertEqual(task.task_id, malicious_id)
        self.assertEqual(task.title, malicious_title)

        # Confirm table still exists and stats compute accurately
        stats = self.state_mgr.get_summary_stats()
        self.assertEqual(stats["total_discovered"], 1)

    def test_unicode_and_special_chars_in_sandbox(self):
        """Verifies sandbox handles Unicode strings, emojis, and multiline escape characters."""
        unicode_code = (
            "import sys\n"
            "data = sys.stdin.read().strip()\n"
            "print(f'Processed: {data} -> 🚀 \\n\\t\\\\')\n"
        )
        sample_input = "Hello 世界"
        expected_output = "Processed: Hello 世界 -> 🚀 \n\t\\"

        res = self.sandbox.validate_solution(unicode_code, sample_input, expected_output)
        self.assertTrue(res.passed, f"Failed with: stdout='{res.stdout}', expected='{expected_output}', stderr='{res.stderr}'")

    def test_multiline_raw_strings_in_candidate_solution(self):
        """Verifies complex raw regex strings inside code execute cleanly."""
        regex_code = (
            "import re, sys\n"
            "text = sys.stdin.read()\n"
            "matches = re.findall(r'\\b[a-zA-Z]{4}\\b', text)\n"
            "print(' '.join(matches))\n"
        )
        res = self.sandbox.validate_solution(regex_code, "This is a fine test case", "This fine test case")
        self.assertTrue(res.passed)


if __name__ == "__main__":
    unittest.main()
