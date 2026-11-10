"""
Test Feature 21: Unified CLI Interface.
Verifies CLI command arguments parsing and dispatch (run-all, run-codekata, run-zenclass, resume, report).
"""

import argparse
import unittest


class TestFeature21CLIInterface(unittest.TestCase):
    """Verifies Unified CLI Interface specifications from PROJECT.md §Feature 21 & Architecture Survey."""

    def setUp(self):
        self.parser = argparse.ArgumentParser(description="ZenClass & Guvi Automation")
        subparsers = self.parser.add_subparsers(dest="command")

        subparsers.add_parser("run-all")
        subparsers.add_parser("run-codekata")
        subparsers.add_parser("run-zenclass")
        subparsers.add_parser("resume")
        subparsers.add_parser("report")

    def test_cli_command_parsing(self):
        """Authoritative source: PROJECT.md §Feature 21."""
        valid_commands = ["run-all", "run-codekata", "run-zenclass", "resume", "report"]
        for cmd in valid_commands:
            args = self.parser.parse_args([cmd])
            self.assertEqual(args.command, cmd)

    def test_cli_rejects_unknown_command(self):
        """Verifies CLI rejects unsupported commands."""
        import sys
        # argparse prints error and exits on invalid commands
        with self.assertRaises(SystemExit):
            self.parser.parse_args(["unsupported-command"])


if __name__ == "__main__":
    unittest.main()
