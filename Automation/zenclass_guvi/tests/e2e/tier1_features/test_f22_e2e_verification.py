"""
Test Feature 22: Final E2E Suite Verification.
Verifies complete coverage of the 22-feature inventory and runner capability.
"""

import os
import unittest
from tests.e2e.test_runner import FEATURE_MAP, TIER_DIRS, TESTS_DIR


class TestFeature22E2EVerification(unittest.TestCase):
    """Verifies Final E2E Suite Verification specifications from PROJECT.md §Feature 22 & Milestone 6."""

    def test_feature_map_contains_all_22_features(self):
        """Authoritative source: PROJECT.md §Feature Inventory (22 features)."""
        self.assertEqual(len(FEATURE_MAP), 22)
        for i in range(1, 23):
            key = f"F{i:02d}"
            self.assertIn(key, FEATURE_MAP, f"Feature {key} missing from FEATURE_MAP")

    def test_tier_directories_exist(self):
        """Verifies all 4 tier test directories are physically present."""
        for tier_num, dir_name in TIER_DIRS.items():
            dir_path = os.path.join(TESTS_DIR, dir_name)
            self.assertTrue(os.path.isdir(dir_path), f"Tier directory {dir_path} missing")


if __name__ == "__main__":
    unittest.main()
