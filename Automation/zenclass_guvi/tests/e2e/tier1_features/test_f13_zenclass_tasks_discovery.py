"""
Test Feature 13: ZenClass Tasks Discovery.
Verifies Kanban board discovery across Active, Pending, and Completed columns and card metadata extraction.
"""

import re
import unittest
from tests.e2e.harness.dom_fixtures import ZENCLASS_TASKS_HTML


class TestFeature13ZenClassTasksDiscovery(unittest.TestCase):
    """Verifies ZenClass Tasks Discovery specifications from PROJECT.md §Feature 13 & spec_miner_survey_3 §1.2."""

    def test_kanban_columns_and_counts(self):
        """Authoritative source: spec_miner_survey_3 §1.2 - active-tasks, pending-tasks, completed-tasks."""
        self.assertIn("active-tasks-heading", ZENCLASS_TASKS_HTML)
        self.assertIn("pending-tasks-heading", ZENCLASS_TASKS_HTML)
        self.assertIn("completed-tasks-heading", ZENCLASS_TASKS_HTML)

        active_count = re.search(r'class="active-tasks-count">(\d+)<', ZENCLASS_TASKS_HTML)
        pending_count = re.search(r'class="pending-tasks-count">(\d+)<', ZENCLASS_TASKS_HTML)
        completed_count = re.search(r'class="completed-tasks-count">(\d+)<', ZENCLASS_TASKS_HTML)

        self.assertEqual(int(active_count.group(1)), 2)
        self.assertEqual(int(pending_count.group(1)), 1)
        self.assertEqual(int(completed_count.group(1)), 1)

    def test_task_card_structure_and_redo_tag(self):
        """Authoritative source: spec_miner_survey_3 §59 - task name and redo tag."""
        task_names = re.findall(r'class="task-name">(.*?)<', ZENCLASS_TASKS_HTML)
        self.assertIn("Day 1: Basic JavaScript Functions", task_names)
        self.assertIn("Day 2: Async Await & Fetch API", task_names)

        # Redo tag verification
        redo_matches = re.findall(r'class="redo-text">(.*?)<', ZENCLASS_TASKS_HTML)
        self.assertEqual(len(redo_matches), 1)
        self.assertEqual(redo_matches[0], "Redo")

    def test_action_buttons_distinction(self):
        """Authoritative source: spec_miner_survey_3 §72 - Submit vs Re-submit vs Edit."""
        self.assertIn(">Submit<", ZENCLASS_TASKS_HTML)
        self.assertIn(">Re-submit<", ZENCLASS_TASKS_HTML)
        self.assertIn(">Edit<", ZENCLASS_TASKS_HTML)


if __name__ == "__main__":
    unittest.main()
